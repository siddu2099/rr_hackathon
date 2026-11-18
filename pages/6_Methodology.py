"""
Page 6: Analytical Methodology & Theoretical Foundations
Complete, transparent mathematical and statistical documentation for the SupeRR Selector S2 framework.
"""
import streamlit as st
import pandas as pd

from app.config import (
    COLOR_BATTING,
    COLOR_BOWLING,
    COLOR_CARD_BG,
    TOTAL_DELIVERIES_EXPECTED,
    PRESSURE_RECORDS_EXPECTED,
    PRESSURE_BATTER_BF_EXPECTED,
    PRESSURE_BOWLER_LEGAL_EXPECTED,
    MATCHES_PLAYED_EXPECTED,
    BAT_PRIOR_MU,
    BAT_PRIOR_N0,
    BOWL_PRIOR_MU,
    BOWL_PRIOR_B0,
    PRESSURE_THRESHOLD
)
from app.components import (
    render_header,
    render_sidebar_footer,
    apply_custom_css
)

apply_custom_css()
render_sidebar_footer()

render_header(
    title="Analytical Methodology & Governance",
    subtitle="Full mathematical specifications, scoring formulas, Empirical Bayes shrinkage, and data governance.",
    badge="Methodological Manifesto"
)

# Section 1: Core Research Philosophy
st.markdown("### 1. Core Philosophy: Operationalizing Match Pressure")
st.markdown(r"""
A fundamental tenet of this framework is that **pressure is an objective property of the match state, not an unobserved psychological trait**.
We operationalize pressure using strictly **lagged, pre-delivery game state variables** to ensure zero future data leakage.

Every delivery in the 200,999-ball database is assigned a continuous pressure score $P \in [0, 100]$.
Deliveries with **$P \ge 45.0$** are classified as **High Pressure**, representing **26,735 deliveries (13.30% of the tournament universe)**.
""")

st.markdown("---")

# Section 2: Mathematical Formulations
col_f1, col_f2 = st.columns(2)

with col_f1:
    st.markdown(f"<h4 style='color: {COLOR_BATTING};'>First-Innings Pressure Model (Setting)</h4>", unsafe_allow_html=True)
    st.latex(r"P_1 = 15 + 20 \cdot \mathbf{1}_{W \ge 3} + 15 \cdot \mathbf{1}_{\text{collapse}} + 25 \cdot \max\left(0, \frac{R_{\text{par}} - R_{\text{proj}}}{R_{\text{par}}}\right) + 25 \cdot \left(\frac{\text{over}}{20}\right)")
    st.markdown(r"""
    - **Resource Scarcity:** Evaluates wicket loss relative to remaining balls ($R_{\text{par}} = 165.0$).
    - **Collapse Penalty ($\mathbf{1}_{\text{collapse}}$):** 
      - *Acute Collapse:* Loss of $\ge 2$ wickets in the previous 12 deliveries.
      - *Structural Collapse:* Loss of $\ge 3$ wickets inside the powerplay (overs 1–6).
    - **Key Invariant:** First-innings pressure is driven by defensive recovery and collapse risk, **never** by required run rate.
    """)

with col_f2:
    st.markdown(f"<h4 style='color: {COLOR_BOWLING};'>Second-Innings Pressure Model (Chasing)</h4>", unsafe_allow_html=True)
    st.latex(r"P_2 = 25 \cdot \min\left(2.5, \frac{\text{RRR}}{\text{CRR}_0}\right) + 25 \cdot \left(\frac{W_{\text{lost}}}{10}\right) + 25 \cdot \left(1 - \frac{B_{\text{rem}}}{120}\right) + 25 \cdot L(B)")
    st.markdown(r"""
    - **Scoring Demand:** Ratio of Required Run Rate ($\text{RRR}$) to initial target run rate ($\text{CRR}_0$).
    - **Wicket Penalty:** Wickets lost exponentially narrow viable winning paths.
    - **Chasing Leverage $L(B)$:** Smooth continuous decay function scaling leverage as remaining balls decrease:
      - Continuous formulation eliminates piecewise boundary discontinuities at overs 10 and 14.
    """)

st.markdown("---")

# Section 3: The BPRI Composite Scoring Architecture
st.markdown("### 2. Player Performance Evaluation: Multi-Dimensional BPRI")
st.markdown("""
Evaluating players strictly by raw strike rate or economy produces severe bias: it rewards volatile single-match outliers and ignores consistent execution.
The **Batting Performance Rating Index (BPRI)** and **Bowling Performance Rating Index (BPRI_bowl)** integrate four complementary dimensions:
""")

c_w1, c_w2 = st.columns(2)

with c_w1:
    st.markdown(f"#### Batting BPRI Weights ({COLOR_BATTING})")
    st.markdown(r"""
    1. **Execution (35%):** Empirical Bayes shrunk pressure strike rate + dot-ball avoidance + boundary generation.
    2. **Clutch Lift (25%):** Unbiased $\Delta\text{SR} = \text{SR}_{P \ge 45} - \text{SR}_{P < 45}$ (evaluated strictly against non-pressure performance).
    3. **Consistency (25%):** Percentage of pressure match innings achieving $\text{SR} \ge 140.0$.
    4. **Volume (15%):** Logarithmic scaling of pressure balls faced to stabilize against small-sample noise.
    """)

with c_w2:
    st.markdown(f"#### Bowling BPRI Weights ({COLOR_BOWLING})")
    st.markdown(r"""
    1. **Containment (35%):** Empirical Bayes shrunk pressure economy rate.
    2. **Wickets (25%):** Pressure bowling strike rate (balls per bowler dismissal).
    3. **Clutch Lift (20%):** Unbiased $\Delta\text{Econ} = \text{Econ}_{P < 45} - \text{Econ}_{P \ge 45}$ (run suppression margin).
    4. **Consistency & Volume (20%):** Percentage of spells conceded $\le 8.50\text{ RPO}$ + logarithmic legal ball scaling.
    """)

st.markdown("---")

# Section 4: Empirical Bayes Normal-Normal Shrinkage
st.markdown("### 3. Empirical Bayes Shrinkage Formulation")
st.markdown("""
To prevent low-sample noise from corrupting rankings while preserving genuine elite outperformance, 
rate metrics are shrunk toward global tournament priors via conjugate Normal-Normal models:
""")

st.latex(r"\mu_{\text{post}} = w \cdot \bar{y} + (1 - w) \cdot \mu_0, \quad \text{where } w = \frac{n}{n + N_0}")

st.markdown(rf"""
- **Batting Priors:** Global Prior Mean $\mu_0 = {BAT_PRIOR_MU:.2f}$, Prior Weight $N_0 = {BAT_PRIOR_N0:.2f}$ balls faced.
- **Bowling Priors:** Global Prior Mean $\mu_0 = {BOWL_PRIOR_MU:.2f}$, Prior Weight $B_0 = {BOWL_PRIOR_B0:.2f}$ legal balls.
- **Shrinkage Behavior:** A batter with 50 balls receives weight $w \approx 0.64$; a batter with 300 balls receives $w \approx 0.91$.
""")

st.markdown("---")

# Section 5: Cricket Law Accounting Matrix
st.markdown("### 4. Cricket Law Accounting Rules (MCC Law 22 & 24)")
st.markdown("""
Accurate rate calculation demands strict alignment with official cricket scoring rules:
""")

acc_data = {
    "Metric Category": ["Total Delivery Records", "Normal Deliveries", "Wides", "No-balls (Overstep + Other)", "Leg-byes", "Byes", "Penalty", "Bowler Legal Deliveries", "Batter Balls Faced"],
    "Full Dataset Count": [f"{TOTAL_DELIVERIES_EXPECTED:,}", "189,167", "7,714", "840", "2,748", "529", "1", "192,444", "193,285"],
    "Pressure Subset (P >= 45)": [f"{PRESSURE_RECORDS_EXPECTED:,}", "24,826", "1,217", "160", "394", "138", "0", f"{PRESSURE_BOWLER_LEGAL_EXPECTED:,}", f"{PRESSURE_BATTER_BF_EXPECTED:,}"],
    "MCC Accounting Rule": [
        "Complete event rows",
        "Fair deliveries without extras",
        "Excluded from balls faced & legal balls (MCC Law 22)",
        "Counted as balls faced; excluded from legal balls (MCC Law 24)",
        "Counted as balls faced & legal balls (extras to team)",
        "Counted as balls faced & legal balls (extras to team)",
        "Non-delivery administrative record",
        "Normal + Leg-byes + Byes",
        "Total Deliveries - Wides"
    ]
}
st.table(pd.DataFrame(acc_data))

st.info(r"""
**Discrepancy Resolution:**  
The exact count of batter balls faced under pressure is **25,518**. 
The number 25,876 that appeared in earlier report text was an isolated clerical typing subtraction error ($26,735 - 859 = 25,876$). 
All data processing scripts strictly evaluated `df[df['is_batter_ball']]`, which sums across all 724 batters to exactly **25,518** ($\Delta = 0$). 
Downstream ranking impact is **0.00%**.
""")

st.markdown("---")

# Section 6: Limitations & Scientific Epistemic Boundaries
st.markdown("### 5. Methodological Limitations & Epistemic Boundaries")
st.markdown(r"""
1. **Operationalized Proxy vs Psychological Trait:** Scoreboard leverage measures match stakes, not player heart rate, anxiety, or an innate biological 'clutch gene'.
2. **Opportunity & Survivorship Bias:** Batting position dictates pressure frequency; players who struggle under pressure are dropped, creating natural survivorship bias in career samples.
3. **Contextual Confounders:** Dew in second innings, pitch deterioration, boundary dimensions, and match-up tactics cannot be completely eliminated.
4. **Sample Size Ceiling in Franchise T20:** High-pressure situations constitute only $13.3\%$ of deliveries. Even across 4 seasons, elite players face only $100\text{--}350$ pressure balls.
5. **Descriptive vs Predictive:** The model evaluates **historical, context-adjusted value delivery**. It is not an auction valuation model or guarantee of future performance.
""")
