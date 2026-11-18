"""
Page 1: Overview & Landscape
Macro tournament coverage, pressure distribution, and benchmark leaderboards.
"""
import streamlit as st
import pandas as pd

from app.config import (
    COLOR_BATTING,
    COLOR_BOWLING,
    TOTAL_DELIVERIES_EXPECTED,
    PRESSURE_RECORDS_EXPECTED,
    PRESSURE_BATTER_BF_EXPECTED,
    PRESSURE_BOWLER_LEGAL_EXPECTED,
    MATCHES_PLAYED_EXPECTED,
    COMPETITIONS_EXPECTED,
    BATTER_QUALIFIED_COUNT,
    BOWLER_QUALIFIED_COUNT,
    PRESSURE_THRESHOLD
)
from app.components import (
    render_header,
    render_kpi,
    render_sidebar_footer,
    apply_custom_css
)
from app.data_loader import (
    load_top10_batters,
    load_top10_bowlers,
    load_deliveries_pressure
)
from app.charts import (
    create_pressure_distribution_chart,
    create_bpri_ranking_chart
)

apply_custom_css()
render_sidebar_footer()

render_header(
    title="Overview: Macro Tournament Scope & Pressure Landscape",
    subtitle="Verified aggregate metrics, continuous match pressure distribution, and top-tier leaderboards.",
    badge="Phase 1 & 2 Synthesis"
)

# Macro KPI Cards Row 1
k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi("Total Deliveries", f"{TOTAL_DELIVERIES_EXPECTED:,}", "Across 867 Played Matches", border_accent=COLOR_BOWLING)
with k2:
    render_kpi("High-Pressure Deliveries", f"{PRESSURE_RECORDS_EXPECTED:,}", f"P >= {PRESSURE_THRESHOLD} (13.30% of Total)", border_accent=COLOR_BATTING)
with k3:
    render_kpi("Pressure Batter Balls Faced", f"{PRESSURE_BATTER_BF_EXPECTED:,}", "Excludes 1,217 Wides (MCC Law 22)", border_accent=COLOR_BATTING)
with k4:
    render_kpi("Pressure Bowler Legal Balls", f"{PRESSURE_BOWLER_LEGAL_EXPECTED:,}", "Excludes Wides & No-balls", border_accent=COLOR_BOWLING)

# Macro KPI Cards Row 2
k5, k6, k7, k8 = st.columns(4)
with k5:
    render_kpi("Scheduled Matches", "883", "867 Played (16 Abandoned)", border_accent=COLOR_BOWLING)
with k6:
    render_kpi("Competitions Covered", f"{COMPETITIONS_EXPECTED}", "IPL, T20I, PSL, BBL, CPL, SA20", border_accent=COLOR_BOWLING)
with k7:
    render_kpi("Qualified Batters", f"{BATTER_QUALIFIED_COUNT}", "Threshold: >= 50 Pressure BF", border_accent=COLOR_BATTING)
with k8:
    render_kpi("Qualified Bowlers", f"{BOWLER_QUALIFIED_COUNT}", "Threshold: >= 60 Pressure Legal Balls", border_accent=COLOR_BOWLING)

st.markdown("---")

# Section 1: Pressure Score Distribution
st.markdown("### 📊 Continuous Pressure Distribution (P ∈ [0, 100])")
st.markdown(r"""
Pressure is operationalized from pre-delivery match context (score, wickets lost, par score projection, and remaining chase demand).
Deliveries are partitioned into four objective tiers:
- **Low Pressure ($P < 20$):** 105,422 balls ($52.45\%$) — routine early overs and low-leverage situations.
- **Moderate Pressure ($20 \le P < 45$):** 68,842 balls ($34.25\%$) — standard middle-over phase.
- **High Pressure ($45 \le P < 70$):** 21,958 balls ($10.92\%$) — steep chasing demand and collapse situations.
- **Critical Pressure ($P \ge 70$):** 4,777 balls ($2.38\%$) — extreme death chases and match-defining finishes.
- **Primary Threshold:** **High Pressure is defined as $P \ge 45.0$** (26,735 deliveries, $13.30\%$).
""")

# Load delivery subset for pressure score distribution
df_deliv = load_deliveries_pressure(columns=['pressure_score', 'pressure_tier', 'is_pressure_delivery'])
fig_dist = create_pressure_distribution_chart(df_deliv)
st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("---")

# Section 2: Top 10 Batting & Bowling Leaderboards Side by Side
st.markdown("### 🏅 Official Top 10 BPRI Composite Leaderboards")
st.markdown("Evaluated via multi-dimensional composite models stabilized by Empirical Bayes Normal-Normal shrinkage.")

c_left, c_right = st.columns(2)

with c_left:
    st.markdown(f"<h4 style='color: {COLOR_BATTING};'>Batting Pressure Rating Index (BPRI)</h4>", unsafe_allow_html=True)
    df_bat = load_top10_batters()
    fig_bat = create_bpri_ranking_chart(df_bat, discipline="batting")
    st.plotly_chart(fig_bat, use_container_width=True)
    st.caption("Weights: Execution (35%) + Clutch Lift (25%) + Consistency (25%) + Volume (15%).")

with c_right:
    st.markdown(f"<h4 style='color: {COLOR_BOWLING};'>Bowling Pressure Rating Index (BPRI_bowl)</h4>", unsafe_allow_html=True)
    df_bowl = load_top10_bowlers()
    fig_bowl = create_bpri_ranking_chart(df_bowl, discipline="bowling")
    st.plotly_chart(fig_bowl, use_container_width=True)
    st.caption("Weights: Containment (35%) + Wickets (25%) + Clutch Lift (20%) + Consistency & Volume (20%).")

st.markdown("---")

# Section 3: Pressure vs Non-Pressure Contrast Card
st.markdown("### ⚖️ The Essence of Clutch: Pressure vs. Non-Pressure Performance")
st.markdown(r"""
A critical principle of the framework is that **career average or strike rate is not an indicator of pressure performance**.
Many prolific anchors score rapidly in low-pressure conditions but stall under rising required run rates.
Conversely, elite finishers like **Rinku Singh**, **Tim David**, and **Jos Buttler** demonstrate substantial **positive clutch lift** ($\Delta\text{SR} > +30.0$).
On the bowling side, **Abrar Ahmed**, **Mohammad Nabi**, and **Gerald Coetzee** suppress scoring by $>3.0\text{ RPO}$ compared to their non-pressure baselines.
""")
