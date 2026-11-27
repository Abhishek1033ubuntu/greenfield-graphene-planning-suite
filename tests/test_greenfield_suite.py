# Co-developed by Abhishek Singh with Google Gemini assistance.
# Run with: python -m unittest tests/test_greenfield_suite.py

import unittest

from src.core_skids_and_utilities import (
    Chiller30TRCurve,
    MacroEquipmentSkid,
    ScheduledConstraintWindow,
    UPS100KVACurve,
    VacuumPumpSkidCurve,
)
from src.custom_system_builder import build_custom_system_type
from src.expansion_and_us_market import evaluate_expansion_and_integration, evaluate_us_market_and_tariff_case
from src.sizing_buffers_and_validation import (
    evaluate_plant_utilities_and_closure,
    simulate_90day_overlapping_constraints,
    size_track_pods,
    validate_simulation_against_pilot,
    verify_cvd_quench_physics,
)


class TestGreenfieldGrapheneSuite(unittest.TestCase):
    def setUp(self):
        self.skid_t2 = MacroEquipmentSkid("EQ-T2-ECHEM", "8-Cell EChem Skid", 14.0, 12.5, 12.5, "kg", 0.85)
        self.vac = VacuumPumpSkidCurve("EQ-VAC-ROOTS-500", 500.0, 20.0, 0.01, 11.0, 2.2)
        self.chiller = Chiller30TRCurve("EQ-UTIL-CHILL-30TR")
        self.ups_2x = UPS100KVACurve("EQ-UTIL-UPS-100KVA", parallel_units=2)

    def test_quench_physics_passes_limit(self):
        res = verify_cvd_quench_physics()
        self.assertEqual(res["status"], "PASS")
        self.assertAlmostEqual(res["quench_time_to_150C_s"], 5.34, places=2)

    def test_utility_closure_and_ups_parallel_sizing(self):
        out = evaluate_plant_utilities_and_closure(117.9, 99.3, 0.5, 36.0, self.vac, self.chiller, self.ups_2x)
        self.assertFalse(out["ups_system"]["overload_flag"])
        self.assertAlmostEqual(out["vacuum"]["elec_kw"], 8.95, places=2)

    def test_90day_overlapping_constraints_saves_cost(self):
        constraints = [
            ScheduledConstraintWindow("C1", "Precursor", 25, 38, 0.35),
            ScheduledConstraintWindow("C2", "Utility", 33, 44, 0.25),
        ]
        res = simulate_90day_overlapping_constraints(90, 35.0, self.skid_t2, 4, 1.0, constraints, 14, 3.0, 70.0, 0.25)
        self.assertEqual(res["unmet_proactive"], 0.0)
        self.assertAlmostEqual(res["net_savings"], 3738.66, places=2)

    def test_expansion_and_us_tariff_dominance(self):
        exp = evaluate_expansion_and_integration(0.86, 2, True, 186912.0, 140000.0, 320000.0, 135000.0, 260000.0, 170000.0, True)
        self.assertTrue(exp["horizontal_pod_scale_out"])
        self.assertTrue(exp["regional_satellite_pod"])
        self.assertTrue(exp["backward_integration_recommended"])
        us = evaluate_us_market_and_tariff_case(785726.3)
        self.assertGreater(us["import_tariff_exposure_usd_yr"], us["power_rate_gap_usd_yr"] * 20)

    def test_golden_lot_validation_and_custom_systems(self):
        val = validate_simulation_against_pilot([23.8, 24.1, 23.9, 24.0], [23.2, 24.5, 23.5, 24.3], "Yield")
        self.assertEqual(val["validation_status"], "PASS")
        sys_pilot = build_custom_system_type("TYPE_I_PILOT")
        self.assertEqual(sys_pilot["total_installed_pods"], 3)


if __name__ == "__main__":
    unittest.main()
