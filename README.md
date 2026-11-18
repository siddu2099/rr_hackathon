# SupeRR Selector Season 2 — Pressure Performance Analysis Dashboard

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.54.0-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-6.5.2-3F4F75.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An interactive, competition-grade cricket analytics dashboard built for **Rajasthan Royals SupeRR Selector Season 2**. Evaluates 200,999 delivery records across 867 played T20 matches (2022–2026) to identify the **Top 10 Batters** and **Top 10 Bowlers** who deliver under high match pressure ($P \ge 45.0$).

---

## 1. Project Overview & Philosophy

Traditional cricket analytics relies heavily on career averages and aggregate strike rates, which often mask poor performance in high-stakes situations. The **SupeRR Selector Season 2 Framework**:
- **Operationalizes Pressure:** Derives a continuous index $P \in [0, 100]$ strictly from **pre-delivery match context** (zero future data leakage).
- **Innings Differentiation:** Evaluates defensive resource depletion and collapse risk in the 1st innings ($R_{\text{par}} = 165$), and required run rate demand ($\text{RRR}/\text{CRR}_0$) with continuous chasing leverage $L(B)$ in the 2nd innings.
- **Empirical Bayes Normal-Normal Shrinkage:** Stabilizes rates against small-sample variance, ensuring that small-sample flukes do not displace proven multi-season match winners.
- **Multi-Dimensional BPRI:** Ranks contenders across **Execution (35%)**, **Clutch Lift (20–25%)**, **Consistency (20–25%)**, and **Sample Volume (15–20%)**.

---

## 2. Technology Stack

- **Frontend & Dashboard Engine:** [Streamlit](https://streamlit.io/) (Multi-page architecture, responsive layout, custom dark sports theme).
- **Interactive Visualizations:** [Plotly Express & Graph Objects](https://plotly.com/) (Dynamic tooltips, scatter quadrants, timelines, ranking bars).
- **Data Engineering:** [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) (Memory-efficient downcasting, vectorized filtering, aggregations).
- **Statistical Modeling:** [SciPy](https://scipy.org/) (Normal-Normal conjugate shrinkage models, robust baselines).
- **Testing & Verification:** [Pytest](https://docs.pytest.org/) (Automated schema, benchmark, and mathematical validation).

---

## 3. Dashboard Architecture & Pages

The application is structured as a modular multi-page Streamlit dashboard:

```text
superr-selector-s2/
│
├── streamlit_app.py            # Main application portal & executive summary
│
├── app/                        # Core application modules
│   ├── __init__.py             # Package declaration
│   ├── config.py               # Constants, theme colors, and relative paths
│   ├── data_loader.py          # Cached memory-efficient CSV loaders (@st.cache_data)
│   ├── data_validation.py      # Benchmark and integrity validators
│   ├── analytics.py            # Filtering, rate computations, and profile extractors
│   ├── charts.py               # Standardized Plotly figure builders
│   └── components.py           # Reusable HTML/CSS cards and layout widgets
│
├── pages/                      # Multi-page dashboard modules
│   ├── 1_Overview.py           # Tournament scope, KPIs, and macro pressure distribution
│   ├── 2_Batting_Analytics.py   # Top 10 batters, filters, clutch lift scatter, quadrant charts
│   ├── 3_Bowling_Analytics.py   # Top 10 bowlers, run suppression ΔEcon, containment charts
│   ├── 4_Pressure_Explorer.py   # Situational explorer and forensic match timelines
│   ├── 5_Player_Analysis.py     # Deep-dive scouting profiles (Pressure vs Non-Pressure)
│   └── 6_Methodology.py        # Mathematical equations, accounting laws, and limitations
│
├── data/
│   ├── raw/                    # Original raw datasets (preserved and untouched)
│   └── processed/              # Validated canonical CSV files (deliveries, rankings, features)
│
├── assets/                     # High-resolution chart graphics and visual assets
│
├── tests/                      # Automated test suite
│   ├── test_data_validation.py # Data integrity and benchmark checks
│   └── test_analytics.py       # Filtering, profiling, and chart tests
│
├── .streamlit/
│   ├── config.toml             # Custom theme and server settings
│   └── secrets.toml            # Placeholder template (no secrets required)
│
├── requirements.txt            # Pinned dependency manifest
├── deployment_checklist.md     # Cloud readiness audit checklist
├── .gitignore                  # Git tracking rules
└── README.md                   # Project documentation
```

### Page Breakdown
1. **Overview:** High-level tournament KPIs (200,999 deliveries, 867 played matches, 138 competitions), continuous pressure distribution ($P \in [0, 100]$ across 4 tiers), and Top 10 leaderboards.
2. **Batting Analytics:** Leaderboards for 153 qualified batters ($\ge 50$ pressure balls), interactive sliders, Pressure SR vs Non-Pressure SR scatter, and Boundary % vs Dot % quadrants.
3. **Bowling Analytics:** Leaderboards for 133 qualified bowlers ($\ge 60$ legal balls), strict positive run suppression convention ($\Delta\text{Econ} = \text{Econ}_{\text{NP}} - \text{Econ}_{\text{P}}$), and containment scatters.
4. **Pressure Explorer:** Situational filtering across overs, innings, and pressure tiers. Includes forensic ball-by-ball chase timelines for iconic matches (e.g. Rinku Singh's 5-six miracle in Match 20193, Jos Buttler's 107* in Match 31250, Abrar Ahmed's death choke in Match 31227).
5. **Player Analysis:** Side-by-side scouting profiles contrasting Career vs High Pressure ($P \ge 45$) vs Non-Pressure ($P < 45$) performance, with match-by-match logs.
6. **Methodology:** Complete mathematical equations, Empirical Bayes shrinkage equations, cricket accounting rules (MCC Law 22 vs Law 24: 25,518 pressure balls faced), and non-causal epistemic framing.

---

## 4. Canonical Benchmark Rankings

### Top 10 Batters Under Pressure ($P \ge 45.0, \text{BF} \ge 50$)
1. **Rinku Singh** — BPRI: **86.40** | 253 BF | 478 Runs | SR: 188.93 | $\Delta$SR: +45.13 | Bdry: 29.3%
2. **Tim David** — BPRI: **86.36** | 305 BF | 585 Runs | SR: 191.80 | $\Delta$SR: +18.84 | Bdry: 26.6%
3. **Tristan Stubbs** — BPRI: **81.77** | 251 BF | 442 Runs | SR: 176.10 | $\Delta$SR: +34.10 | Bdry: 23.5%
4. **Naman Dhir** — BPRI: **81.65** | 90 BF | 183 Runs | SR: 203.33 | $\Delta$SR: +41.21 | Bdry: 30.0%
5. **David Miller** — BPRI: **81.33** | 229 BF | 421 Runs | SR: 183.84 | $\Delta$SR: +42.07 | Bdry: 26.6%
6. **Jos Buttler** — BPRI: **80.49** | 55 BF | 118 Runs | SR: 214.55 | $\Delta$SR: +60.33 | Bdry: 30.9%
7. **Tilak Varma** — BPRI: **80.08** | 260 BF | 446 Runs | SR: 171.54 | $\Delta$SR: +31.85 | Bdry: 21.9%
8. **Dhruv Jurel** — BPRI: **79.28** | 112 BF | 208 Runs | SR: 185.71 | $\Delta$SR: +40.08 | Bdry: 27.7%
9. **Ravindra Jadeja** — BPRI: **78.75** | 207 BF | 334 Runs | SR: 161.35 | $\Delta$SR: +33.52 | Bdry: 19.8%
10. **MS Dhoni** — BPRI: **78.46** | 227 BF | 377 Runs | SR: 166.08 | $\Delta$SR: +32.18 | Bdry: 24.2%

### Top 10 Bowlers Under Pressure ($P \ge 45.0, \text{Legal Balls} \ge 60$)
1. **Abrar Ahmed** — BPRI: **86.42** | 141 Balls | 8 Wickets | Econ: 3.83 | $\Delta$Econ: +3.35 | Dot: 55.3%
2. **Mohammad Nabi** — BPRI: **79.70** | 65 Balls | 5 Wickets | Econ: 4.52 | $\Delta$Econ: +4.11 | Dot: 50.8%
3. **Mohammad Nawaz** — BPRI: **79.03** | 121 Balls | 10 Wickets | Econ: 5.16 | $\Delta$Econ: +2.15 | Dot: 47.9%
4. **Sunil Narine** — BPRI: **78.63** | 168 Balls | 12 Wickets | Econ: 5.29 | $\Delta$Econ: +1.66 | Dot: 48.2%
5. **Kuldeep Yadav** — BPRI: **78.56** | 206 Balls | 26 Wickets | Econ: 6.26 | $\Delta$Econ: +1.79 | Dot: 49.0%
6. **Shadab Khan** — BPRI: **77.61** | 113 Balls | 9 Wickets | Econ: 5.47 | $\Delta$Econ: +2.66 | Dot: 42.5%
7. **Sufiyan Muqeem** — BPRI: **76.51** | 130 Balls | 15 Wickets | Econ: 5.35 | $\Delta$Econ: +0.80 | Dot: 53.8%
8. **Gerald Coetzee** — BPRI: **76.19** | 71 Balls | 9 Wickets | Econ: 6.00 | $\Delta$Econ: +3.29 | Dot: 52.1%
9. **Akeal Hosein** — BPRI: **75.86** | 116 Balls | 9 Wickets | Econ: 5.79 | $\Delta$Econ: +1.89 | Dot: 43.1%
10. **Rashid Khan** — BPRI: **74.65** | 405 Balls | 35 Wickets | Econ: 6.58 | $\Delta$Econ: +0.91 | Dot: 44.7%

---

## 5. Local Installation & Execution

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Git

### 1. Clone or Open the Repository
```bash
git clone https://github.com/<your-username>/superr-selector-s2.git
cd superr-selector-s2
```

### 2. Create and Activate a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Automated Test Suite
Verify that all data integrity, benchmark, and analytics tests pass:
```bash
python -m pytest tests/
```

### 5. Launch the Dashboard
```bash
python -m streamlit run streamlit_app.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 6. Streamlit Community Cloud Deployment

The repository is pre-configured for zero-configuration deployment to [Streamlit Community Cloud](https://streamlit.io/cloud):

1. **Push to GitHub:**
   Commit all files and push the repository to GitHub:
   ```bash
   git add .
   git commit -m "feat: complete interactive cricket analytics dashboard"
   git push origin main
   ```
2. **Connect to Streamlit Cloud:**
   - Log in to [share.streamlit.io](https://share.streamlit.io/).
   - Click **"Create app"**.
   - Select your GitHub repository and branch (`main`).
   - Set **Main file path** to `streamlit_app.py`.
3. **Deploy:**
   - Click **"Deploy!"**.
   - No external secrets, databases, or API keys are required.
   - The app will automatically build and launch at your public Streamlit URL.

---

## 7. Data Accounting & Integrity Invariants

All delivery numbers in this project have been audited and verified:
- **Total Deliveries:** `200,999`
- **Pressure Deliveries ($P \ge 45$):** `26,735`
- **Pressure Batter Balls Faced:** `25,518` (MCC Law 22: $26,735 - 1,217\text{ wides}$).
- **Pressure Bowler Legal Deliveries:** `25,358` (MCC Law 24: $26,735 - 1,217\text{ wides} - 160\text{ no-balls}$).
- **No Typo Artifacts:** The typographical subtraction error `25,876` from earlier report drafts is completely eliminated.
- **Sign Convention:** Bowling $\Delta\text{Econ}$ strictly follows $\text{Econ}_{\text{NP}} - \text{Econ}_{\text{P}}$, where positive values denote superior run suppression.

---

## 8. Known Limitations & Epistemic Boundaries

1. **Proxy Nature of Scoreboard Pressure:** Match-state leverage operationalizes pressure through situational urgency. It is an objective proxy for match stakes, not a biometric measurement of player stress or heart rate.
2. **Opportunity & Tactical Selection:** Low-order finishers naturally experience more pressure opportunities than opening anchors. Players who fail under pressure are dropped, creating natural survivorship bias.
3. **Sample Size Realities:** High-pressure deliveries constitute $13.3\%$ of cricket deliveries. Even elite multi-season players accumulate only $100\text{--}350$ pressure balls, which is why Empirical Bayes shrinkage is indispensable.
4. **Descriptive, Not Predictive:** Rankings measure **historical context-adjusted value delivery**, not future auction valuation or form projection.
