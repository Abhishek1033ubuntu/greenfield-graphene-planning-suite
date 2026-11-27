# Co-developed by Abhishek Singh with Google Gemini assistance.
# Scope: Expansion/vertical-integration triggers and US demand / site / tariff evaluation.

import math
from typing import Dict


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
        "horizontal_pod_scale_out": (sustained_util_frac >= util_trigger and consecutive_quarters_above_trig >= 2)
        or contract_tranche_locked,
        "regional_satellite_pod": tariff_or_transit_penalty_yr > satellite_net_cost_yr,
        "backward_integration_payback_yrs": round(payback_yrs, 2) if math.isfinite(payback_yrs) else None,
        "backward_integration_recommended": payback_yrs <= max_payback_years,
        "forward_integration_net_benefit_yr": round(forward_margin_uplift_yr - forward_incremental_cost_yr, 2),
        "forward_integration_recommended": (forward_margin_uplift_yr > forward_incremental_cost_yr) and customer_offtake_committed,
    }


def evaluate_us_market_and_tariff_case(
    annual_grid_kwh: float,
    us_hub_tariff_usd_kwh: float = 0.10,
    hybrid_tariff_usd_kwh: float = 0.11,
    annual_capture_revenue_usd: float = 3_894_000.0,
    imported_value_share: float = 0.40,
    import_tariff_rate: float = 0.12,
) -> Dict:
    us_elec_cost = annual_grid_kwh * us_hub_tariff_usd_kwh
    hybrid_elec_cost = annual_grid_kwh * hybrid_tariff_usd_kwh
    tariff_exposure = annual_capture_revenue_usd * imported_value_share * import_tariff_rate
    power_spread = hybrid_elec_cost - us_elec_cost
    return {
        "annual_grid_kwh": round(annual_grid_kwh, 1),
        "us_hub_elec_cost_usd_yr": round(us_elec_cost, 2),
        "hybrid_elec_cost_usd_yr": round(hybrid_elec_cost, 2),
        "power_rate_gap_usd_yr": round(power_spread, 2),
        "import_tariff_exposure_usd_yr": round(tariff_exposure, 2),
        "tariff_to_power_gap_ratio": round(tariff_exposure / max(0.01, power_spread), 1),
    }
