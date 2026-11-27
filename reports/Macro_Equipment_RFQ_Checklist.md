# Macro-Equipment Request for Quotation (RFQ) Checklist

**Author:** Abhishek Singh  
**ORCID:** https://orcid.org/0009-0004-6913-096X  
**GitHub:** https://github.com/Abhishek1033ubuntu  
**AI Collaboration:** Co-developed with Google Gemini assistance  

## Scope Rule (No Piece-Part BOMs)
Specify **functional throughput envelopes, performance curves, utility interfaces, metrology/safety hooks, and FAT/SAT acceptance guarantees**. Leave sub-millimeter mechanical dimensions, fasteners, and internal piece-part BOMs to certified OEM builders.

## Process & Utility Skids Required
1. **Track 1 (`EQ-T1-R2RCVD` — R2R Vacuum Joule-CVD Skid):** $\ge 25.0\,\text{m}^2/\text{day}$ nameplate, $\ge 85\%$ availability, $0.02\text{–}100\,\text{mbar}$ operating range, Helium quench cooling ($1000\,^\circ\text{C} \rightarrow < 150\,^\circ\text{C}$ in $\le 12.0\,\text{s}$), and inline inspection ports aligned to **ISO/TS 80004-13**, **ISO/TS 21356-1**, and **IEC/TS 62607**.
2. **Track 2 (`EQ-T2-ECHEM` — 8-Cell EChem + Ultrasonic & Distillation Skid):** $\ge 12.5\,\text{kg/day}$ nameplate, $\ge 85\%$ availability, closed-loop solvent/coagulant recovery, jacket cooling interface $\le 12.5\,\text{kW}_{\text{th}}$, and inline dispersion/flake metrology hooks.
3. **Track 3A (`EQ-T3A-VLAM` — Vacuum Wafer Laminator & RIE Skid):** $\ge 150.0\,\text{wafers/day}$ nameplate, $\ge 88\%$ availability, cleanroom-compatible handling, and wafer-level electrical/surface verification hooks.
4. **Track 3B (`EQ-T3B-GCNT` — Co-Axial G/CNT Spinning Skid):** $\ge 2.5\,\text{km/day}$ nameplate, $\ge 85\%$ availability, continuous tension/draw control, and inline conductivity/resistance monitoring.
5. **Vacuum Skid (`EQ-VAC-ROOTS-500`):** Certified effective pumping speed $S_{\text{eff}}(P)$ across `100 mbar` down to `0.01 mbar` base pressure, Roots booster cut-in pressure, gas throughput ($\text{mbar}\cdot\text{m}^3/\text{h}$), and idle vs. rated electrical draw ($\text{kW}$).
6. **30 TR Process Chiller (`EQ-UTIL-CHILL-30TR`):** Certified $105.51\,\text{kW}_{\text{th}}$ ($30\,\text{TR}$) cooling capacity, part-load $\text{kW/TR}$ curve, high-ambient derating up to $\ge 44\,^\circ\text{C}$, and `N+1` chilled-water loop readiness.
7. **100 kVA Double-Conversion UPS (`EQ-UTIL-UPS-100KVA`):** Certified $\ge 0.90\,\text{PF}$ ($90.0\,\text{kW}$ real max per unit), double-conversion efficiency curve, parallel/`N+1` bus support, and battery ride-through runtime curve.
