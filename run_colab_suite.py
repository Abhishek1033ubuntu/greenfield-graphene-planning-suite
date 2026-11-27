import json
import pandas as pd


def run_master_greenfield_suite(export_prefix: str = "greenfield_graphene_master"):
    skid_t1 = MacroEquipmentSkid("EQ-T1-R2RCVD", "Roll-in-Vacuum Joule-CVD Skid", 18.5, 16.0, 25.0, "m2", 0.85)
    skid_t2 = MacroEquipmentSkid("EQ-T2-ECHEM", "8-Cell EChem + Ultrasonic Skid", 14.0, 12.5, 12.5, "kg", 0.85)
    skid_t3a = MacroEquipmentSkid("EQ-T3A-VLAM", "Vacuum Wafer Laminator & RIE Skid", 9.5, 6.5, 150.0, "wafers", 0.88)
    skid_t3b = MacroEquipmentSkid("EQ-T3B-GCNT", "Co-Axial G/CNT Spinning Skid", 13.5, 9.5, 2.5, "km", 0.85)

    fleet = [
        size_track_pods(60.0, skid_t1, trim_yield=0.95, redundancy="N+1"),
        size_track_pods(30.0, skid_t2, trim_yield=1.00, redundancy="N+1"),
        size_track_pods(120.0, skid_t3a, trim_yield=0.96, redundancy="N+1"),
        size_track_pods(2.0, skid_t3b, trim_yield=0.98, redundancy="none"),
    ]
    total_pods = sum(x["installed_pods"] for x in fleet)
    total_proc_elec = round(sum(x["elec_kw"] for x in fleet), 2)
    total_proc_cool = round(sum(x["cooling_kw_th"] for x in fleet), 2)

    quench = verify_cvd_quench_physics()
    vac = VacuumPumpSkidCurve("EQ-VAC-ROOTS-500", 500.0, 20.0, 0.01, 11.0, 2.2)
    chill = Chiller30TRCurve("EQ-UTIL-CHILL-30TR")
    ups = UPS100KVACurve("EQ-UTIL-UPS-100KVA", parallel_units=2)
    utilities = evaluate_plant_utilities_and_closure(total_proc_elec, total_proc_cool, 0.5, 36.0, vac, chill, ups)

    constraints = [
        ScheduledConstraintWindow("CON-01-PRECURSOR", "Raw Material Allocation Cut", 25, 38, 0.35),
        ScheduledConstraintWindow("CON-02-UTILITY", "Chiller/Grid Maintenance Window", 33, 44, 0.25),
    ]
    c90 = simulate_90day_overlapping_constraints(90, 35.0, skid_t2, 4, 1.0, constraints, 14, 3.0, 70.0, 0.25)

    expansion = evaluate_expansion_and_integration(
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

    calibration = validate_simulation_against_pilot(
        sim_values=[23.8, 24.1, 23.9, 24.0],
        actual_pilot_values=[23.2, 24.5, 23.5, 24.3],
        metric_name="Track_1_Daily_Qualified_Yield_m2",
        max_allowed_mape_pct=5.0,
    )

    report = {
        "fleet_summary": {
            "total_pods": total_pods,
            "process_elec_kw": total_proc_elec,
            "process_cooling_kw_th": total_proc_cool,
            "tracks": fleet,
        },
        "quench_verification": quench,
        "oem_utilities": utilities,
        "constraint_90d": c90,
        "expansion_advisor": expansion,
        "golden_lot_calibration": calibration,
    }

    with open(f"{export_prefix}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    pd.json_normalize(report, sep="_").to_csv(f"{export_prefix}.csv", index=False)
    print(f"Exported {export_prefix}.json and {export_prefix}.csv successfully.")
    return report
