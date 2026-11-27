# Co-developed by Abhishek Singh with Google Gemini assistance.
# Scope: Macro-skid and central utility performance curves (no mechanical piece-part BOMs).

from dataclasses import dataclass
import math
from typing import Dict

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
        assert 0.0 < self.availability <= 1.0, "Availability must be in (0, 1]"
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
        assert elec_kw >= self.idle_power_kw * 0.99, "Vacuum pump power below idle floor"
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
        assert cooling_demand_kw_th >= 0.0, "Cooling demand cannot be negative"
        cap_kw_th = self.nameplate_cooling_kw_th()
        plr = cooling_demand_kw_th / cap_kw_th
        ambient_factor = 1.0 + 0.012 * max(-15.0, ambient_temp_c - self.design_ambient_c)
        if plr <= 1e-6:
            comp_kw = 0.0
        else:
            plr_eff_curve = 0.72 + 0.28 * (plr ** 1.15)
            comp_kw = (cooling_demand_kw_th / KW_PER_TR) * self.nominal_kw_per_tr * plr_eff_curve * ambient_factor
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
        assert self.parallel_units >= 1, "At least one UPS module is required"
        return self.rated_kva * self.power_factor * self.parallel_units

    def efficiency(self, load_frac: float) -> float:
        x = min(1.2, max(0.01, load_frac))
        eta = 0.956 - 0.08 * ((x - 0.60) ** 2) - 0.012 * max(0.0, x - 1.0)
        return max(0.80, min(0.965, eta))

    def evaluate_load(self, critical_load_kw: float) -> Dict[str, float]:
        assert critical_load_kw >= 0.0, "Critical load cannot be negative"
        max_kw = self.max_real_kw()
        load_frac = critical_load_kw / max_kw
        eta = self.efficiency(load_frac)
        input_kw = critical_load_kw / eta if critical_load_kw > 0 else 0.0
        loss_kw = input_kw - critical_load_kw
        total_batt_kwh = self.battery_kwh_usable * self.parallel_units
        runtime_min = (total_batt_kwh * 0.85 / max(0.5, critical_load_kw)) * 60.0 if critical_load_kw > 0 else 999.0
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
