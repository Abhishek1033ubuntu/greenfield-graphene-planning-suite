import math
from dataclasses import dataclass
from typing import Dict, List
import numpy as np

KW_PER_TR = 3.51685284


@dataclass
class MacroEquipmentSkid:
    skid_id: str
    name: str
    rated_elec_kw: float
    rated_cooling_kw_th: float
    nameplate_capacity_per_day: float
    unit: str
    availability: float = 0.85

    def effective_daily_capacity(self) -> float:
        return self.nameplate_capacity_per_day * self.availability


@dataclass
class ScheduledConstraintWindow:
    constraint_id: str
    constraint_type: str
    start_day: int
    end_day: int
    capacity_reduction_frac: float


@dataclass
class VacuumPumpSkidCurve:
    skid_id: str
    s_max_m3_hr: float
    p_roots_on_mbar: float
    p_base_mbar: float
    rated_power_kw: float
    idle_power_kw: float

    def effective_pumping_speed_m3_hr(self, pressure_mbar: float) -> float:
        assert pressure_mbar > 0.0, "Chamber/line pressure must be positive (mbar)"
        if pressure_mbar <= self.p_base_mbar:
            return 0.0
        span = max(1e-9, math.log10(self.p_roots_on_mbar / self.p_base_mbar))
        pos = min(1.0, max(0.0, math.log10(pressure_mbar / self.p_base_mbar) / span))
        smooth = pos * pos * (3.0 - 2.0 * pos)
        viscous_factor = 1.0 / (1.0 + max(0.0, (pressure_mbar - 10.0) / 200.0))
        return max(0.0, min(self.s_max_m3_hr, self.s_max_m3_hr * (0.25 + 0.75 * smooth) * viscous_factor))

    def evaluate_pressure(self, pressure_mbar: float) -> Dict[str, float]:
        s_eff = self.effective_pumping_speed_m3_hr(pressure_mbar)
        load_ratio = min(1.0, max(0.0, s_eff / max(1e-9, self.s_max_m3_hr)))
        elec_kw = self.idle_power_kw + (self.rated_power_kw - self.idle_power_kw) * (0.35 + 0.65 * load_ratio)
        return {
            "skid_id": self.skid_id,
            "pressure_mbar": pressure_mbar,
            "s_eff_m3_hr": round(s_eff, 2),
            "throughput_mbar_m3_hr": round(s_eff * pressure_mbar, 4),
            "elec_kw": round(elec_kw, 2),
        }


@dataclass
class Chiller30TRCurve:
    skid_id: str
    rated_tr: float = 30.0
    nominal_kw_per_tr: float = 0.85
    pump_power_kw: float = 3.2
    design_ambient_c: float = 35.0

    def nameplate_cooling_kw_th(self) -> float:
        return self.rated_tr * KW_PER_TR

    def evaluate_load(self, cooling_demand_kw_th: float, ambient_temp_c: float = 35.0) -> Dict[str, float]:
        assert cooling_demand_kw_th >= 0.0
        cap_kw_th = self.nameplate_cooling_kw_th()
        plr = cooling_demand_kw_th / cap_kw_th
        ambient_factor = 1.0 + 0.012 * max(-15.0, ambient_temp_c - self.design_ambient_c)
        comp_kw = (
            0.0
            if plr <= 1e-6
            else (cooling_demand_kw_th / KW_PER_TR) * self.nominal_kw_per_tr * (0.72 + 0.28 * (plr ** 1.15)) * ambient_factor
        )
        return {
            "skid_id": self.skid_id,
            "nameplate_cooling_kw_th": round(cap_kw_th, 2),
            "cooling_demand_kw_th": round(cooling_demand_kw_th, 2),
            "part_load_ratio": round(plr, 3),
            "ambient_temp_c": ambient_temp_c,
            "total_elec_kw": round(comp_kw + self.pump_power_kw, 2),
            "overloaded": cooling_demand_kw_th > cap_kw_th,
        }


@dataclass
class UPS100KVACurve:
    skid_id: str
    rated_kva: float = 100.0
    power_factor: float = 0.90
    battery_kwh_usable: float = 45.0
    parallel_units: int = 1

    def max_real_kw(self) -> float:
        return self.rated_kva * self.power_factor * self.parallel_units

    def efficiency(self, load_frac: float) -> float:
        x = min(1.2, max(0.01, load_frac))
        eta = 0.956 - 0.08 * ((x - 0.60) ** 2) - 0.012 * max(0.0, x - 1.0)
        return max(0.80, min(0.965, eta))

    def evaluate_load(self, critical_load_kw: float) -> Dict[str, float]:
        assert critical_load_kw >= 0.0
        max_kw = self.max_real_kw()
        load_frac = critical_load_kw / max_kw if max_kw > 0 else 0.0
        eta = self.efficiency(load_frac)
        input_kw = critical_load_kw / eta if critical_load_kw > 0 else 0.0
        loss_kw = input_kw - critical_load_kw
        runtime_min = ((self.battery_kwh_usable * self.parallel_units) * 0.85 / max(0.5, critical_load_kw)) * 60.0 if critical_load_kw > 0 else 999.0
        return {
            "skid_id": self.skid_id,
            "parallel_units": self.parallel_units,
            "max_real_kw": round(max_kw, 2),
            "critical_load_kw": round(critical_load_kw, 2),
            "load_frac_pct": round(load_frac * 100.0, 1),
            "double_conv_eff_pct": round(eta * 100.0, 2),
            "input_grid_kw": round(input_kw, 2),
            "heat_loss_kw": round(loss_kw, 2),
            "est_battery_runtime_min": round(runtime_min, 1),
            "overload_flag": critical_load_kw > max_kw,
        }


def size_track_pods(daily_target: float, skid: MacroEquipmentSkid, trim_yield: float = 0.95, redundancy: str = "N+1") -> Dict:
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
) -> Dict:
    tau_th = (rho_kg_m3 * cp_j_kgk * foil_thickness_m) / h_he_quench
    t_quench_s = -tau_th * math.log((temp_safe_c - temp_ambient_c) / (temp_start_c - temp_ambient_c))
    assert t_quench_s < 12.0, f"SIM-05 FAIL: Quench time {t_quench_s:.2f}s exceeds 12.0s limit"
    return {
        "thermal_time_constant_s": round(tau_th, 3),
        "quench_time_to_150C_s": round(t_quench_s, 2),
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


def evaluate_expansion_and_integration(
    sustained_util_frac: float,
    consecutive_quarters_above_trig: int,
    contract_tranche_locked: bool,
    tariff_or_transit_penalty_yr: float,
    satellite_net_cost_yr: float,
    backward_capex_net: float,
    annual_recovery_savings_yr: float,
    forward_margin_uplift_yr: float,
    forward_incremental_cost_yr: float,
    customer_offtake_committed: bool,
    util_trigger: float = 0.83,
    max_payback_years: float = 3.0,
) -> Dict:
    payback_yrs = (backward_capex_net / annual_recovery_savings_yr) if annual_recovery_savings_yr > 0 else float("inf")
    return {
        "horizontal_pod_scale_out": (sustained_util_frac >= util_trigger and consecutive_quarters_above_trig >= 2) or contract_tranche_locked,
        "regional_satellite_pod": tariff_or_transit_penalty_yr > satellite_net_cost_yr,
        "backward_integration_payback_yrs": round(payback_yrs, 2) if math.isfinite(payback_yrs) else None,
        "backward_integration_recommended": payback_yrs <= max_payback_years,
        "forward_integration_net_benefit_yr": round(forward_margin_uplift_yr - forward_incremental_cost_yr, 2),
        "forward_integration_recommended": (forward_margin_uplift_yr > forward_incremental_cost_yr) and customer_offtake_committed,
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
