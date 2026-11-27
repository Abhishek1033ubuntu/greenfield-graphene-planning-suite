# Changelog

All notable changes to **Modular Greenfield Graphene Manufacturing Facility: Systems Architecture, Simulation Framework & Custom Configuration Suite** (`greenfield-graphene-planning-suite`) are documented in this file.

**Author:** Abhishek Singh (ORCID: https://orcid.org/0009-0004-6913-096X)  
**AI Collaboration:** Co-developed with Google Gemini assistance (see `AI_COLLABORATION.md`)  
**Scope Boundary:** Systems-level pod sizing, macro-skid curves, utility redundancy, scheduled buffers, expansion governance, and ISO/IEC validation only (no piece-part BOMs).

## [1.0.0] - 2026-11-27

### Added
* **Four Modular Process Tracks (`src/core_skids_and_utilities.py`, `src/sizing_buffers_and_validation.py`):**
  * Track 1 (`EQ-T1-R2RCVD` — Roll-in-Vacuum Joule-CVD Film Skid), Track 2 (`EQ-T2-ECHEM` — 8-Cell EChem + Ultrasonic & Distillation Skid), Track 3A (`EQ-T3A-VLAM` — Vacuum Wafer Laminator & RIE Skid), and Track 3B (`EQ-T3B-GCNT` — Co-Axial G/CNT Spinning Skid).
  * Scaling across Lean Pilot (`3 pods`), Contract Ramp (`7 pods`), and Full Baseline (`11 pods`).
* **Macro Utility & Redundancy Curves (`src/core_skids_and_utilities.py`):**
  * `VacuumPumpSkidCurve` (`EQ-VAC-ROOTS-500`) from `100 mbar` down to `0.01 mbar` base pressure.
  * `Chiller30TRCurve` (`EQ-UTIL-CHILL-30TR`, `105.51 kW_th` nominal at `1 TR = 3.51685 kW_th`) with part-load and ambient lift up to `44 °C`, plus `N+1` peak thermal sizing (`150.0 kW_th`).
  * `UPS100KVACurve` (`EQ-UTIL-UPS-100KVA`, `90.0 kW` real at `0.90 PF`) with parallel and `2+1` (`N+1`) load/runtime evaluation.
* **Constraint Buffering, Expansion Logic & US Market/Tariff Model (`src/sizing_buffers_and_validation.py`, `src/expansion_and_us_market.py`):**
  * 90-day multi-window overlapping constraint pre-build optimizer and standby pod promotion checks.
  * Horizontal scale-out, regional satellite finishing, backward/forward vertical integration payback (`<= 3.0 years`), and US demand/tariff sensitivity evaluation.
* **Custom System Builders & Validation Gates (`src/custom_system_builder.py`, `tests/test_greenfield_suite.py`):**
  * `build_custom_system_type()` supporting Custom System Types I–IV (`TYPE_I_PILOT`, `TYPE_II_SC15`, `TYPE_III_ICSPEC`, `TYPE_IV_USHYB`).
  * `SIM-05` Helium quench check and blind Golden-Lot `MAPE <= 5.0%` validation aligned to **ISO/TS 80004-13**, **ISO/TS 21356-1**, and **IEC/TS 62607**.
* **Reports, Notebook & Export Artifacts (`reports/`, `notebooks/`, `exports/`, `CITATION.cff`, `AI_COLLABORATION.md`, `References.md`):**
  * Full Work Report (`GGF-ENG-RPT-2026-V1`), Technical Feasibility Report, Macro-Equipment RFQ Checklist, Colab notebook, and JSON/CSV simulation exports.
