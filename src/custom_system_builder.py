from typing import Dict
from src.core_skids_and_utilities import (
    Chiller30TRCurve,
    MacroEquipmentSkid,
    ScheduledConstraintWindow,
    UPS100KVACurve,
    VacuumPumpSkidCurve,
)
from src.expansion_and_us_market import evaluate_expansion_and_integration
from src.sizing_buffers_and_validation import (
    simulate_90day_overlapping_constraints,
    size_track_pods,
)


def build_custom_system_type(system_type: str) -> Dict:
    """
    Assembles one of four custom greenfield graphene facility configurations
    using standardized macro skids, utility curves, and buffer/expansion rules:
      - "TYPE_I_PILOT"    : Lean Pilot & Metrology Qualification Line (3 pods)
      - "TYPE_II_SC15"    : 15-Year Phased Superconducting & Conductor Line (scales to 11 pods)
      - "TYPE_III_ICSPEC" : High-Precision IC-Level Specimen Batch Line (4-5 pods)
      - "TYPE_IV_USHYB"   : Forecasted US-Capture Hybrid Split-Track Facility (11-12 pods)
    """
    key = system_type.strip().upper()

    skid_t1 = MacroEquipmentSkid("EQ-T1-R2RCVD", "Roll-in-Vacuum Joule-CVD Skid", 18.5, 16.0, 25.0, "m2", 0.85)
    skid_t2 = MacroEquipmentSkid("EQ-T2-ECHEM", "8-Cell EChem + Ultrasonic Skid", 14.0, 12.5, 12.5, "kg", 0.85)
    skid_t3a = MacroEquipmentSkid("EQ-T3A-VLAM", "Vacuum Wafer Laminator & RIE Skid", 9.5, 6.5, 150.0, "wafers", 0.88)
    skid_t3b = MacroEquipmentSkid("EQ-T3B-GCNT", "Co-Axial G/CNT Spinning Skid", 13.5, 9.5, 2.5, "km", 0.85)

    vac = VacuumPumpSkidCurve("EQ-VAC-ROOTS-500", 500.0, 20.0, 0.01, 11.0, 2.2)
    chiller = Chiller30TRCurve("EQ-UTIL-CHILL-30TR")

    if key == "TYPE_I_PILOT":
        tracks = [
            size_track_pods(15.0, skid_t1, trim_yield=0.95, redundancy="none"),
            size_track_pods(8.0, skid_t2, trim_yield=1.00, redundancy="none"),
            size_track_pods(80.0, skid_t3a, trim_yield=0.96, redundancy="none"),
        ]
        ups = UPS100KVACurve("EQ-UTIL-UPS-100KVA", parallel_units=1)
        chiller_plan = "1 active + 1 standby (2 x 30 TR)"
        buffer_note = "2-day normal coupon buffer; gate expansion on Golden-Lot MAPE <= 5.0%"
        expansion_plan = "Hold horizontal scale-out until blind Golden-Lot calibration passes"

    elif key == "TYPE_II_SC15":
        tracks = [
            size_track_pods(35.0, skid_t2, trim_yield=1.00, redundancy="N+1"),
            size_track_pods(3.5, skid_t3b, trim_yield=0.96, redundancy="N+1"),
        ]
        ups = UPS100KVACurve("EQ-UTIL-UPS-100KVA", parallel_units=3)
        chiller_plan = "2 active + 1 standby (3 x 30 TR) at peak phase"
        buffer_note = "3.0-day normal buffer + 14-day pre-build window for overlapping cuts"
        expansion_plan = evaluate_expansion_and_integration(
            sustained_util_frac=0.86,
            consecutive_quarters_above_trig=2,
            contract_tranche_locked=True,
            tariff_or_transit_penalty_yr=120000.0,
            satellite_net_cost_yr=150000.0,
            backward_capex_net=320000.0,
            annual_recovery_savings_yr=135000.0,
            forward_margin_uplift_yr=190000.0,
            forward_incremental_cost_yr=140000.0,
            customer_offtake_committed=True,
        )

    elif key == "TYPE_III_ICSPEC":
        tracks = [
            size_track_pods(12.0, skid_t1, trim_yield=0.72, redundancy="N+1"),
            size_track_pods(120.0, skid_t3a, trim_yield=0.94, redundancy="N+1"),
        ]
        ups = UPS100KVACurve("EQ-UTIL-UPS-100KVA", parallel_units=2)
        chiller_plan = "1 active + 1 standby (2 x 30 TR)"
        buffer_note = "2.0-day cleanroom buffer + 12-day pre-build ahead of carrier changeovers"
        expansion_plan = evaluate_expansion_and_integration(
            sustained_util_frac=0.78,
            consecutive_quarters_above_trig=1,
            contract_tranche_locked=False,
            tariff_or_transit_penalty_yr=175000.0,
            satellite_net_cost_yr=125000.0,
            backward_capex_net=260000.0,
            annual_recovery_savings_yr=80000.0,
            forward_margin_uplift_yr=260000.0,
            forward_incremental_cost_yr=170000.0,
            customer_offtake_committed=True,
        )

    elif key == "TYPE_IV_USHYB":
        tracks = [
            size_track_pods(60.0, skid_t1, trim_yield=0.95, redundancy="N+1"),
            size_track_pods(30.0, skid_t2, trim_yield=1.00, redundancy="N+1"),
            size_track_pods(120.0, skid_t3a, trim_yield=0.96, redundancy="N+1"),
            size_track_pods(2.0, skid_t3b, trim_yield=0.98, redundancy="none"),
        ]
        ups = UPS100KVACurve("EQ-UTIL-UPS-100KVA", parallel_units=3)
        chiller_plan = "2 active + 1 standby (3 x 30 TR) for up to 150 kW_th @ 40-44 C"
        buffer_note = "3.0-day domestic bulk + 5.0-day regional finishing buffer"
        expansion_plan = evaluate_expansion_and_integration(
            sustained_util_frac=0.86,
            consecutive_quarters_above_trig=2,
            contract_tranche_locked=True,
            tariff_or_transit_penalty_yr=186912.0,
            satellite_net_cost_yr=140000.0,
            backward_capex_net=320000.0,
            annual_recovery_savings_yr=135000.0,
            forward_margin_uplift_yr=260000.0,
            forward_incremental_cost_yr=170000.0,
            customer_offtake_committed=True,
        )
    else:
        raise ValueError(f"Unknown system_type '{system_type}'. Choose TYPE_I_PILOT, TYPE_II_SC15, TYPE_III_ICSPEC, or TYPE_IV_USHYB.")

    sample_90d = simulate_90day_overlapping_constraints(
        horizon_days=90,
        daily_demand=28.0,
        skid=skid_t2,
        active_pods=3,
        trim_yield=1.0,
        constraints=[
            ScheduledConstraintWindow("CON-01-PRECURSOR", "Precursor Cut", 25, 38, 0.35),
            ScheduledConstraintWindow("CON-02-UTILITY", "Utility Window", 33, 44, 0.25),
        ],
        prebuild_lead_days=14,
        normal_buffer_days=3.0,
        unit_margin=65.0,
        daily_holding_cost=0.20,
    )

    return {
        "system_type": key,
        "scope_boundary": "Macro skids & system envelopes only; no mechanical piece-part BOMs.",
        "ai_collaboration": "Co-developed by Abhishek Singh with Google Gemini assistance.",
        "total_installed_pods": sum(t["installed_pods"] for t in tracks),
        "process_elec_kw": round(sum(t["elec_kw"] for t in tracks), 2),
        "process_cooling_kw_th": round(sum(t["cooling_kw_th"] for t in tracks), 2),
        "tracks": tracks,
        "vacuum_skid": vac.skid_id,
        "chiller_plan": chiller_plan,
        "ups_max_real_kw": ups.max_real_kw(),
        "buffer_policy": buffer_note,
        "sample_90d_constraint_check": sample_90d,
        "expansion_and_integration": expansion_plan,
    }
