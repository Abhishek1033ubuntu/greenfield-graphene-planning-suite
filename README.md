# Modular Greenfield Graphene Manufacturing Facility — Planning & Simulation Suite

[![ORCID](https://img.shields.io/badge/ORCID-0009--0004--6913--096X-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0004-6913-096X)
[![GitHub](https://img.shields.io/badge/GitHub-Abhishek1033ubuntu-181717?logo=github&logoColor=white)](https://github.com/Abhishek1033ubuntu)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Google Colab](https://img.shields.io/badge/Google%20Colab-Ready-F9AB00?logo=googlecolab&logoColor=black)](https://colab.research.google.com/)
[![Standards](https://img.shields.io/badge/Standards-ISO%2FTS%2080004--13%20%7C%2021356--1%20%7C%20IEC%2FTS%2062607-0F766E)](References.md)
[![AI Collaboration](https://img.shields.io/badge/AI%20Collaboration-Google%20Gemini-4285F4?logo=googlegemini&logoColor=white)](AI_COLLABORATION.md)
[![Scope](https://img.shields.io/badge/Scope-Macro%20Skids%20Only%20(No%20Part%20BOMs)-4B5563)](README.md)

**Principal Author:** Abhishek Singh | UIDAI: 9414 9122 9013  
**ORCID:** https://orcid.org/0009-0004-6913-096X  
**GitHub:** https://github.com/Abhishek1033ubuntu  
**Support / Sponsorship:** https://www.paypal.me/Abhishek1033ubuntu  
**AI Collaboration:** Co-developed with Google Gemini assistance (see [AI_COLLABORATION.md](AI_COLLABORATION.md))

---

## 1. Project Overview & Scope Boundary

This repository provides a modular production-planning, utility-closure, constraint-buffering, and validation framework for a **Greenfield Graphene Manufacturing Facility** (`GGF-ENG-RPT-2026-V1`).

* **Systems-Level Planning Boundary:** All models operate strictly at the **pod, macro-skid, utility envelope, scheduled buffer, and expansion governance** level. Sub-millimeter mechanical dimensions, flange geometries, and piece-part Bills of Materials (BOMs) are explicitly excluded and remain the responsibility of certified OEM equipment builders.
* **Four Modular Process Tracks:**
  * **Track 1 (`EQ-T1-R2RCVD`):** Roll-to-Roll Vacuum Joule-CVD Film Skid (`25.0 m<sup>2</sup>/day` nameplate, `85.0%` availability, `21.25 m<sup>2</sup>/day` effective).
  * **Track 2 (`EQ-T2-ECHEM`):** 8-Cell Electrochemical + Ultrasonic & Distillation Skid (`12.5 kg/day` nameplate, `85.0%` availability, `10.625 kg/day` effective).
  * **Track 3A (`EQ-T3A-VLAM`):** Cleanroom Vacuum Wafer Laminator & RIE Skid (`150.0 wafers/day` nameplate, `88.0%` availability, `132.0 wafers/day` effective).
  * **Track 3B (`EQ-T3B-GCNT`):** Co-Axial Graphene/CNT Spinning Skid (`2.5 km/day` nameplate, `85.0%` availability, `2.125 km/day` effective).
* **Macro Utility Performance Curves:**
  * **Vacuum Pumping (`EQ-VAC-ROOTS-500`):** Effective pumping speed S<sub>eff</sub>(P) and electrical draw from `100 mbar` roughing down to `0.01 mbar` base pressure (`491.21 m<sup>3</sup>/h` and `10.90 kW` at `10.0 mbar`; `320.75 m<sup>3</sup>/h` and `8.95 kW` at `0.5 mbar`).
  * **30 TR Process Chiller (`EQ-UTIL-CHILL-30TR`):** `105.51 kW<sub>th</sub>` nominal cooling (`1 TR = 3.51685 kW<sub>th</sub>`) with part-load ratio and ambient derating up to `44 °C` (`2` active + `1` standby = `3 x 30 TR` for `150.0 kW<sub>th</sub>` peak cooling).
  * **100 kVA Double-Conversion UPS (`EQ-UTIL-UPS-100KVA`):** `90.0 kW` real rating at `0.90 PF` with parallel / `N+1` load sharing (`2 x 100 kVA` parallel or `2+1` `N+1` at `44 °C`).

---

## 2. Updated Repository Structure

```text
greenfield-graphene-planning-suite/
├── README.md                                  # Project overview, badges, repository tree, Custom System Types I-IV & international references
├── LICENSE                                    # Apache-2.0 open-source license
├── References.md                              # International standards (ISO/IEC) & provenance/citation policy
├── AI_COLLABORATION.md                        # Explicit attribution record for Abhishek Singh & Google Gemini
├── requirements.txt                           # Python dependencies (numpy, pandas, matplotlib, reportlab)
│
├── src/
│   ├── __init__.py                            # Package exports across all planning modules
│   ├── core_skids_and_utilities.py            # MacroEquipmentSkid, ScheduledConstraintWindow, VacuumPumpSkidCurve, Chiller30TRCurve, UPS100KVACurve
│   ├── sizing_buffers_and_validation.py       # size_track_pods, verify_cvd_quench_physics, simulate_90day_overlapping_constraints, validate_simulation_against_pilot
│   ├── expansion_and_us_market.py             # evaluate_expansion_and_integration & US market demand / tariff sensitivity model
│   └── custom_system_builder.py               # build_custom_system_type() for Custom System Types I, II, III, and IV
│
├── notebooks/
│   └── greenfield_graphene_colab_master.ipynb # Google Colab notebook running end-to-end simulation and exporting JSON/CSV/PDF
│
├── reports/
│   ├── GGF-ENG-RPT-2026-V1_Full_Work_Report.md
│   ├── Technical_Feasibility_Report.md
│   └── Macro_Equipment_RFQ_Checklist.md
│
├── exports/                                   # Generated simulation & report artifacts
│   ├── .gitkeep
│   ├── greenfield_graphene_master.json
│   ├── greenfield_graphene_master.csv
│   └── Greenfield_Graphene_Full_Work_Report.pdf
│
└── tests/
    └── test_greenfield_suite.py               # Deterministic unit assertions for pod sizing, utility closure, 90-day constraints & MAPE

```

---

## 3. Custom System Configurations (`Types I–IV`)

Using `build_custom_system_type()` in `src/custom_system_builder.py`, four facility configurations can be assembled directly from the modular pods and utility curves:

| System Variant | Code Identifier | Pod Architecture | Utility Redundancy | Primary Optimization Lever |
| --- | --- | --- | --- | --- |
| **Type I: Lean Pilot & Metrology Line** | `TYPE_I_PILOT` | `3 pods` (`Track 1 + 2 + 3A`) | `2 x 30 TR` chillers (`N+1`), `1 x 100 kVA` UPS | Blind Golden-Lot calibration (`MAPE <= 5.0%`) |
| **Type II: 15-Yr Conductor Supply Line** | `TYPE_II_SC15` | `5 -> 8 -> 11 pods` (`Track 2 + 3B`) | `3 x 30 TR` chillers, `2+1` (`3 x 100 kVA`) UPS | 90-day pre-build buffering + solvent/gas recovery |
| **Type III: IC Specimen Batch Line** | `TYPE_III_ICSPEC` | `4 -> 5 pods` (`Track 1 + 3A`) | `2 x 30 TR` chillers, `2 x 100 kVA` parallel UPS | `Track 3A` slack capacity + forward singulation |
| **Type IV: US-Capture Hybrid Facility** | `TYPE_IV_USHYB` | `11 -> 12 pods` (split-node) | `3 x 30 TR` chillers (`150 kW<sub>th</sub>` peak), `2+1` UPS | US import tariff avoidance vs. industrial power spread |

---

## 4. Quick Start & Verification

```bash
# Install dependencies
pip install -r requirements.txt

# Run deterministic unit verification suite
python -m unittest tests/test_greenfield_suite.py

```

---

## 5. International Standards & Institutional References

All nomenclature, structural characterization, electrical key control characteristics (KCCs), and industrial power-rate benchmarks in this suite are anchored to international standards bodies and official statistical agencies:

* **ISO/TS 80004-13:2024 — Nanotechnologies — Vocabulary — Part 13: Graphene and other two-dimensional (2D) materials**
International Organization for Standardization (ISO / TC 229): https://www.iso.org/obp and https://committee.iso.org/home/tc229
* **ISO/TS 21356-1:2021 — Nanotechnologies — Structural characterization of graphene — Part 1: Graphene from powders and dispersions**
International Organization for Standardization (ISO / TC 229): https://www.iso.org/standard/70757.html
* **IEC TS 62607-6-4:2024 — Nanomanufacturing — Key control characteristics — Part 6-4: Graphene — Surface conductance measurement using non-contact microwave resonant cavity**
International Electrotechnical Commission (IEC / TC 113): https://webstore.iec.ch/en/publication/68258
* **IEC TS 62607-6-8:2023 — Nanomanufacturing — Key control characteristics — Part 6-8: Graphene — Sheet resistance: In-line four-point probe**
International Electrotechnical Commission (IEC / TC 113): https://webstore.iec.ch/en/publication/32302
* **IEC TS 62607-6-23:2025 — Nanomanufacturing — Key control characteristics — Part 6-23: Graphene films — Carrier mobility and sheet resistance: Hall Measurement**
International Electrotechnical Commission (IEC / TC 113): https://webstore.iec.ch/en/publication/64056
* **IEC Electropedia — International Electrotechnical Vocabulary (IEV)**
International Electrotechnical Commission (IEC): https://www.electropedia.org/
* **U.S. Energy Information Administration (EIA) — Electric Power Monthly (Industrial Retail Electricity Rates)**
Used to ground US industrial power-rate sensitivity (`~9.52 ¢/kWh` US industrial average in September 2026 vs. `$0.10–$0.11/kWh` all-in site modeling): https://www.eia.gov/electricity/monthly/update/end-use.php
