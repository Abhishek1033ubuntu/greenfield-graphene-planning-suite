# Modular Greenfield Graphene Manufacturing Facility — Planning & Simulation Suite

**Author:** Abhishek Singh  
**ORCID:** https://orcid.org/0009-0004-6913-096X  
**GitHub:** https://github.com/Abhishek1033ubuntu  
**Support / Sponsorship:** https://www.paypal.me/Abhishek1033ubuntu  

## Scope Boundary
This suite models **systems-level pod sizing, macro-skid performance envelopes, utility redundancy, scheduled 90-day overlapping constraints, expansion/vertical-integration triggers, US market/tariff trade-offs, and ISO/IEC pilot validation**.
*Sub-millimeter mechanical dimensions, flange geometries, and piece-part Bills of Materials (BOMs) are explicitly excluded and remain with certified OEM equipment builders.*

## Modular Architecture
* **Track 1 (`EQ-T1-R2RCVD`):** Roll-to-Roll Vacuum Joule-CVD Film Skid (`25.0 m2/day` nameplate, `0.85` availability).
* **Track 2 (`EQ-T2-ECHEM`):** 8-Cell Electrochemical + Ultrasonic & Distillation Skid (`12.5 kg/day` nameplate, `0.85` availability).
* **Track 3A (`EQ-T3A-VLAM`):** Cleanroom Vacuum Wafer Laminator & RIE Skid (`150.0 wafers/day` nameplate, `0.88` availability).
* **Track 3B (`EQ-T3B-GCNT`):** Co-Axial Graphene/CNT Spinning Skid (`2.5 km/day` nameplate, `0.85` availability).

## Macro Utility Curves
* **`VacuumPumpSkidCurve` (`EQ-VAC-ROOTS-500`):** Effective pumping speed $S_{\text{eff}}(P)$ and electrical power across `100 mbar` down to `0.01 mbar` base pressure.
* **`Chiller30TRCurve` (`EQ-UTIL-CHILL-30TR`):** `30 TR` (`105.51 kW_th` nominal at `1 TR = 3.51685 kW_th`) part-load ratio and high-ambient lift curves (`35 C` to `44 C+`).
* **`UPS100KVACurve` (`EQ-UTIL-UPS-100KVA`):** `100 kVA` (`90.0 kW` real at `0.90 PF`) double-conversion efficiency, parallel/`N+1` load sharing, and battery runtime.

## Quick Start in Google Colab
1. Paste `greenfield_graphene_suite.py` into a Colab cell and run.
2. Paste `run_colab_suite.py` into the next cell and call `run_master_greenfield_suite()` to generate `greenfield_graphene_master.json` and `greenfield_graphene_master.csv`.

## Repository Structure

```
greenfield-graphene-planning-suite/
├── README.md                                  # Project overview, scope boundary, Custom System Types I-IV & AI collaboration note
├── LICENSE                                    # Open-science / research license (e.g., Apache-2.0 or CC BY-NC-ND 4.0)
├── References.md                              # Standards (ISO/TS 80004-13, ISO/TS 21356-1, IEC/TS 62607) & provenance/citation policy
├── AI_COLLABORATION.md                        # Explicit record of Google Gemini AI collaboration, human engineering ownership & verification gates
├── requirements.txt                           # Python dependencies (numpy, pandas, matplotlib, reportlab)
│
├── src/
│   ├── __init__.py
│   ├── core_skids_and_utilities.py           # MacroEquipmentSkid, ScheduledConstraintWindow, VacuumPumpSkidCurve, Chiller30TRCurve, UPS100KVACurve
│   ├── sizing_buffers_and_validation.py       # size_track_pods, verify_cvd_quench_physics, simulate_90day_overlapping_constraints, validate_simulation_against_pilot
│   ├── expansion_and_us_market.py             # evaluate_expansion_and_integration & US market demand / tariff sensitivity model
│   └── custom_system_builder.py               # build_custom_system_type() for Custom System Types I, II, III, and IV
│
├── notebooks/
│   └── greenfield_graphene_colab_master.ipynb # Single-run Google Colab notebook executing full pipeline + PDF/JSON/CSV export
│
├── reports/
│   ├── GGF-ENG-RPT-2026-V1_Full_Work_Report.md
│   ├── Technical_Feasibility_Report.md
│   └── Macro_Equipment_RFQ_Checklist.md
│
├── exports/                                   # Generated simulation & report artifacts (JSON, CSV, PDF)
│   ├── .gitkeep
│   ├── greenfield_graphene_master.json
│   ├── greenfield_graphene_master.csv
│   └── Greenfield_Graphene_Full_Work_Report.pdf
│
└── tests/
    └── test_greenfield_suite.py               # Deterministic assertions for pod sizing, utility closure, 90-day constraints & MAPE
```
