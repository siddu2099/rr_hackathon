# Presentation Data Integrity & Numerical Checks

**Audit Execution Date:** November 18, 2026  
**Status:** **ALL MANDATORY CHECKS PASSED**

## Mandatory Numerical Checks Table

| Measure | Expected Value | Observed Data Value | Verification Source | Status |
|---|---:|---:|---|:---:|
| **Total Delivery Records** | 200,999 | 200,999 | `ball_by_ball.csv` / `deliveries_with_pressure.csv` | **PASS** |
| **Pressure Records (`P >= 45`)** | 26,735 | 26,735 | `deliveries_with_pressure.csv` (`is_pressure_delivery == True`) | **PASS** |
| **Pressure Wides** | 1,217 | 1,217 | `deliveries_with_pressure.csv` merged with `extras_type == 'wide'` | **PASS** |
| **Pressure Batter Balls Faced** | 25,518 | 25,518 | `is_batter_ball == True` ($26,735 - 1,217\text{ wides}$) | **PASS** |
| **Pressure Bowler Legal Deliveries** | 25,358 | 25,358 | `is_legal == True` ($26,735 - 1,217\text{ wides} - 160\text{ no-balls}$) | **PASS** |

> [!IMPORTANT]
> **Definitive Accounting Resolution:**  
> The correct pressure batter balls-faced total is definitively **25,518**, not 25,876. The latter was an isolated clerical typing error in earlier prose reports and is strictly banned from all presentation slides, tables, and submission artifacts.

## Canonical Leaderboard Consistency

### Top 10 Batters (from `data/processed/top10_batters.csv`)
- **Rank 1: Rinku Singh** — BPRI: 86.40, Balls: 253, Runs: 478, SR: 188.93, $\Delta$SR: +50.60
- **Rank 2: Tim David** — BPRI: 86.36, Balls: 305, Runs: 585, SR: 191.80, $\Delta$SR: +36.21
- **Rank 3: Tristan Stubbs** — BPRI: 81.77, Balls: 251, Runs: 442, SR: 176.10, $\Delta$SR: +29.21
- **Rank 4: Naman Dhir** — BPRI: 81.65, Balls: 90, Runs: 183, SR: 203.33, $\Delta$SR: +40.00
- **Rank 5: David Miller** — BPRI: 81.33, Balls: 229, Runs: 421, SR: 183.84, $\Delta$SR: +50.29
- **Rank 6: Jos Buttler** — BPRI: 80.49, Balls: 55, Runs: 118, SR: 214.55, $\Delta$SR: +74.88
- **Rank 7: Tilak Varma** — BPRI: 80.08, Balls: 260, Runs: 446, SR: 171.54, $\Delta$SR: +37.66
- **Rank 8: Dhruv Jurel** — BPRI: 79.28, Balls: 112, Runs: 208, SR: 185.71, $\Delta$SR: +44.76
- **Rank 9: Ravindra Jadeja** — BPRI: 78.75, Balls: 207, Runs: 334, SR: 161.35, $\Delta$SR: +31.81
- **Rank 10: MS Dhoni** — BPRI: 78.46, Balls: 227, Runs: 377, SR: 166.08, $\Delta$SR: +32.07

### Top 10 Bowlers (from `data/processed/top10_bowlers.csv`)
- **Rank 1: Abrar Ahmed** — BPRI: 86.42, Legal Balls: 141, Runs Conceded: 90, Econ: 3.83, Wickets: 7, $\Delta$Econ: -3.37
- **Rank 2: Mohammad Nabi** — BPRI: 79.70, Legal Balls: 65, Runs Conceded: 49, Econ: 4.52, Wickets: 3, $\Delta$Econ: -2.33
- **Rank 3: Mohammad Nawaz** — BPRI: 79.03, Legal Balls: 121, Runs Conceded: 104, Econ: 5.16, Wickets: 5, $\Delta$Econ: -3.07
- **Rank 4: Sunil Narine** — BPRI: 78.63, Legal Balls: 168, Runs Conceded: 148, Econ: 5.29, Wickets: 6, $\Delta$Econ: -1.74
- **Rank 5: Kuldeep Yadav** — BPRI: 78.56, Legal Balls: 206, Runs Conceded: 215, Econ: 6.26, Wickets: 11, $\Delta$Econ: -0.66
- **Rank 6: Shadab Khan** — BPRI: 77.61, Legal Balls: 113, Runs Conceded: 103, Econ: 5.47, Wickets: 4, $\Delta$Econ: -2.85
- **Rank 7: Sufiyan Muqeem** — BPRI: 76.51, Legal Balls: 130, Runs Conceded: 116, Econ: 5.35, Wickets: 4, $\Delta$Econ: -1.82
- **Rank 8: Gerald Coetzee** — BPRI: 76.19, Legal Balls: 71, Runs Conceded: 71, Econ: 6.00, Wickets: 5, $\Delta$Econ: -3.05
- **Rank 9: Akeal Hosein** — BPRI: 75.86, Legal Balls: 116, Runs Conceded: 112, Econ: 5.79, Wickets: 4, $\Delta$Econ: -0.71
- **Rank 10: Rashid Khan** — BPRI: 74.65, Legal Balls: 405, Runs Conceded: 444, Econ: 6.58, Wickets: 19, $\Delta$Econ: -0.56

## Bootstrap Artifact Quarantine Protocol
In accordance with Stage 1 audit instructions:
- All bootstrap inferential p-values, bootstrap confidence intervals, and FWER/FDR significance badges are quarantined and excluded from presentation slides.
- The presentation and executive narrative rely strictly on verified descriptive metrics and Empirical Bayes shrinkage estimates.
- Downstream rankings remain 100% invariant.
