# Co-developed by Abhishek Singh with Google Gemini assistance.
# Scope: Pod sizing, SIM-05 thermal quench check, 90-day overlapping constraints & Golden-Lot MAPE validation.

import math
from typing import Dict, List
import numpy as np

from src.core_skids_and_utilities import (
    Chiller30TRCurve,
    MacroEquipmentSkid,
    ScheduledConstraintWindow,
    UPS100KVACurve,
    VacuumPumpSkidCurve,
)


def size_track_pods(
    daily_target: float,
    skid: MacroEquipmentSkid,
    trim_yield: float = 0.95,
    redundancy: str = "N+1",
) -> Dict:
    assert daily_target > 0.0, "Daily target must be positive"
    assert 0.0 < trim_yield <= 1.0, "Trim yield must be in (0, 1]"
    gross_daily_needed = daily_target / trim_yield
    eff_cap_per_pod = skid.effective_daily_capacity()
    active_pods = max(1, math.ceil(gross_daily_needed / eff_cap_per_pod))
    standby_pods = 1 if redundancy == "N+1" else (active_pods if redundancy == "2N" else 0)
    utilization = gross_daily_needed / (active_pods * eff_cap_per_pod)
    elec_kw = active_pods * skid.rated_elec_kw * (0.35 + 0.65 * utilization)
    cooling_kw_th = active_pods * skid.rated_cooling_kw_th * (0.35 + 0.65 * utilization)
    assert cooling_kw_th <= elec_kw * 1.15, f"Energy closure breach on {skid.skid_id}"
    return {
        "skid_id": skid.skid_id,
        "active_pods": active_pods,
        "standby_pods": standby_pods,
        "installed_pods": active_pods + standby_pods,
        "utilization_pct": round(utilization * 100, 1),
        "elec_kw": round(elec_kw, 2),
        "cooling_kw_th": round(cooling_kw_th, 2),
        "unit": skid.unit,
    }


def verify_cvd_quench_physics(
    temp_start_c: float = 1000.0,
    temp_safe_c: float = 150.0,
    temp_ambient_c: float = 35.0,
    foil_thickness_m: float = 25e-6,
    rho_kg_m3: float = 8900.0,
    cp_j_kgk: float = 395.0,
    h_he_quench: float = 35.0,
    max_quench_s: float = 12.0,
) -> Dict:
    tau_th = (rho_kg_m3 * cp_j_kgk * foil_thickness_m) / h_he_quench
    t_quench_s = -tau_th * math.log((temp_safe_c - temp_ambient_c) / (temp_start_c - temp_ambient_c))
    assert t_quench_s < max_quench_s, f"SIM-05 FAIL: Quench time {t_quench_s:.2f}s exceeds {max_quench_s:.1f}s limit"
    return {
        "thermal_time_constant_s": round(tau_th, 3),
        "quench_time_to_150C_s": round(t_quench_s, 2),
        "threshold_s": max_quench_s,
        "status": "PASS",
    }


def simulate_90day_overlapping_constraints(
    horizon_days: int,
    daily_demand: float,
    skid: MacroEquipmentSkid,
    active_pods: int,
    trim_yield: float,
    constraints: List[ScheduledConstraintWindow],
    prebuild_lead_days: int,
    normal_buffer_days: float,
    unit_margin: float,
    daily_holding_cost: float,
) -> Dict:
    gross_demand_per_day = daily_demand / trim_yield
    eff_cap_per_day = active_pods * skid.effective_daily_capacity()

    daily_cap_arr = []
    for d in range(1, horizon_days + 1):
        surviving = 1.0
        for c in constraints:
            if c.start_day <= d <= c.end_day:
                surviving *= max(0.0, 1.0 - c.capacity_reduction_frac)
        daily_cap_arr.append(eff_cap_per_day * surviving)

    constrained_idx = [i for i, cap in enumerate(daily_cap_arr) if cap < gross_demand_per_day]
    total_shortfall = sum(max(0.0, gross_demand_per_day - cap) for cap in daily_cap_arr)
    init_norm_buf = normal_buffer_days * gross_demand_per_day

    inv_r, unmet_r, hold_r = init_norm_buf, 0.0, 0.0
    for cap_d in daily_cap_arr:
        if cap_d >= gross_demand_per_day:
            inv_r += min(cap_d - gross_demand_per_day, max(0.0, init_norm_buf - inv_r))
        else:
            short_d = gross_demand_per_day - cap_d
            used = min(inv_r, short_d)
            inv_r -= used
            unmet_r += (short_d - used)
        hold_r += inv_r * daily_holding_cost

    first_c = (min(constrained_idx) + 1) if constrained_idx else (horizon_days + 1)
    pb_start, pb_end = max(1, first_c - prebuild_lead_days), max(0, first_c - 1)
    avg_hold_u = daily_holding_cost * (max(1, len(constrained_idx)) + 0.5 * prebuild_lead_days)
    allow_pb = unit_margin > avg_hold_u
    target_extra = max(0.0, total_shortfall - init_norm_buf)

    inv_p, pb_added, unmet_p, hold_p = init_norm_buf, 0.0, 0.0, 0.0
    for idx, cap_d in enumerate(daily_cap_arr):
        day_num = idx + 1
        if cap_d >= gross_demand_per_day:
            spare = cap_d - gross_demand_per_day
            to_norm = min(spare, max(0.0, init_norm_buf - inv_p))
            inv_p += to_norm
            rem = spare - to_norm
            if allow_pb and (pb_start <= day_num <= pb_end):
                add_pb = min(rem, max(0.0, target_extra - pb_added))
                inv_p += add_pb
                pb_added += add_pb
        else:
            short_d = gross_demand_per_day - cap_d
            used = min(inv_p, short_d)
            inv_p -= used
            unmet_p += (short_d - used)
        hold_p += inv_p * daily_holding_cost

    loss_r = unmet_r * unit_margin + hold_r
    loss_p = unmet_p * unit_margin + hold_p
    return {
        "constrained_days": len(constrained_idx),
        "prebuild_window": f"Day {pb_start}..Day {pb_end}" if pb_end >= pb_start else "None",
        "total_shortfall": round(total_shortfall, 2),
        "prebuilt_units": round(pb_added, 2),
        "unmet_reactive": round(unmet_r, 2),
        "unmet_proactive": round(unmet_p, 2),
        "total_loss_reactive": round(loss_r, 2),
        "total_loss_proactive": round(loss_p, 2),
        "net_savings": round(loss_r - loss_p, 2),
    }


def evaluate_plant_utilities_and_closure(
    process_elec_kw: float,
    process_cooling_kw_th: float,
    vacuum_pressure_mbar: float,
    ambient_temp_c: float,
    vac_skid: VacuumPumpSkidCurve,
    chiller: Chiller30TRCurve,
    ups: UPS100KVACurve,
) -> Dict:
    vac_res = vac_skid.evaluate_pressure(vacuum_pressure_mbar)
    chill_res = chiller.evaluate_load(process_cooling_kw_th, ambient_temp_c=ambient_temp_c)
    total_critical_kw = process_elec_kw + vac_res["elec_kw"] + chill_res["total_elec_kw"]
    ups_res = ups.evaluate_load(total_critical_kw)
    assert abs(ups_res["input_grid_kw"] - (ups_res["critical_load_kw"] + ups_res["heat_loss_kw"])) < 0.05
    return {
        "vacuum": vac_res,
        "chiller_30tr": chill_res,
        "ups_system": ups_res,
        "total_plant_grid_kw": ups_res["input_grid_kw"],
    }


def validate_simulation_against_pilot(
    sim_values: List[float],
    actual_pilot_values: List[float],
    metric_name: str,
    max_allowed_mape_pct: float = 5.0,
) -> Dict:
    sim_arr = np.array(sim_values, dtype=float)
    act_arr = np.array(actual_pilot_values, dtype=float)
    assert len(sim_arr) == len(act_arr) and len(sim_arr) > 0 and np.all(act_arr != 0)
    mape = float(np.mean(np.abs((act_arr - sim_arr) / act_arr)) * 100.0)
    rmse = float(np.sqrt(np.mean((act_arr - sim_arr) ** 2)))
    return {
        "metric": metric_name,
        "samples": len(sim_arr),
        "mape_pct": round(mape, 2),
        "rmse": round(rmse, 3),
        "threshold_pct": max_allowed_mape_pct,
        "validation_status": "PASS" if mape <= max_allowed_mape_pct else "RECALIBRATE_REQUIRED",
    }
