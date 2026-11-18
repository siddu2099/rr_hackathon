"""
SupeRR Selector Season 2 — Pressure Performance Analysis Dashboard
Main Application Entrypoint.
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
    COMPETITIONS_EXPECTED
)
from app.components import (
    render_header,
    render_kpi,
    render_sidebar_footer,
    apply_custom_css
)
from app.data_loader import (
    load_top10_batters,
    load_top10_bowlers
)

# Page Configuration
st.set_page_config(
    page_title="SupeRR Selector S2 | Pressure Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# Sidebar Branding
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/6/60/Rajasthan_Royals_Logo.svg/1200px-Rajasthan_Royals_Logo.svg.png", width=120) if False else None
st.sidebar.title("SupeRR Selector S2")
st.sidebar.markdown("**Pressure Performance Analysis**")
st.sidebar.info("Navigate through the analytics modules using the sidebar pages above.")
render_sidebar_footer()

# Header
render_header(
    title="SupeRR Selector Season 2: Who Delivers Under Pressure?",
    subtitle="A scientific, leakage-free cricket analytics dashboard evaluating batting and bowling performance under high match pressure.",
    badge="Official Analytics Portal"
)

# Quick Overview Hero Section
st.markdown(r"""
### Welcome to the Rajasthan Royals Pressure Analytics Hub
This dashboard presents the definitive analytical framework and results for **SupeRR Selector Season 2**. 
Using 200,999 deliveries across 867 played T20 matches (2022–2026), we identify the **Top 10 Batters** and **Top 10 Bowlers** 
who excel when match leverage reaches its apex ($P \ge 45.0$).
""")

# Top KPI Row
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    render_kpi("Total Deliveries", f"{TOTAL_DELIVERIES_EXPECTED:,}", "867 Played Matches", border_accent=COLOR_BOWLING)
with col2:
    render_kpi("Pressure Balls", f"{PRESSURE_RECORDS_EXPECTED:,}", "P >= 45.0 (13.30%)", border_accent=COLOR_BATTING)
with col3:
    render_kpi("Batter Balls Faced", f"{PRESSURE_BATTER_BF_EXPECTED:,}", "Excludes 1,217 Wides", border_accent=COLOR_BATTING)
with col4:
    render_kpi("Bowler Legal Balls", f"{PRESSURE_BOWLER_LEGAL_EXPECTED:,}", "Excludes Extras", border_accent=COLOR_BOWLING)
with col5:
    render_kpi("Top Batter", "Rinku Singh", "BPRI: 86.40 (SR 188.9)", border_accent=COLOR_BATTING)
with col6:
    render_kpi("Top Bowler", "Abrar Ahmed", "BPRI: 86.42 (Econ 3.83)", border_accent=COLOR_BOWLING)

st.markdown("---")

# Highlights Row: Top Batters vs Top Bowlers Previews
col_bat, col_bowl = st.columns(2)

with col_bat:
    st.markdown(f"<h3 style='color: {COLOR_BATTING};'>🏆 Top 5 Batters Under Pressure</h3>", unsafe_allow_html=True)
    df_bat = load_top10_batters()
    disp_bat = df_bat[['rank', 'striker_name', 'BPRI_Model1_Balanced', 'p_balls_faced', 'p_strike_rate', 'unbiased_delta_sr']].head(5).copy()
    disp_bat.columns = ['Rank', 'Player Name', 'BPRI Score', 'Pressure BF', 'Pressure SR', 'Clutch Lift (ΔSR)']
    st.dataframe(
        disp_bat.style.format({
            'BPRI Score': '{:.2f}',
            'Pressure SR': '{:.1f}',
            'Clutch Lift (ΔSR)': '+{:.1f}'
        }),
        use_container_width=True,
        hide_index=True
    )
    st.caption("👉 Explore full qualified rankings & scatter plots on the **Batting Analytics** page.")

with col_bowl:
    st.markdown(f"<h3 style='color: {COLOR_BOWLING};'>🎯 Top 5 Bowlers Under Pressure</h3>", unsafe_allow_html=True)
    df_bowl = load_top10_bowlers()
    disp_bowl = df_bowl[['rank', 'bowler_name', 'BPRI_Model1_Balanced', 'p_legal_balls', 'p_economy', 'unbiased_delta_econ']].head(5).copy()
    disp_bowl.columns = ['Rank', 'Player Name', 'BPRI Score', 'Legal Balls', 'Pressure Econ', 'Suppression (ΔEcon)']
    st.dataframe(
        disp_bowl.style.format({
            'BPRI Score': '{:.2f}',
            'Pressure Econ': '{:.2f}',
            'Suppression (ΔEcon)': '{:.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )
    st.caption("👉 Explore full qualified rankings & scatter plots on the **Bowling Analytics** page.")

st.markdown("---")

# Navigation Guidance Cards
st.markdown("### 🧭 Dashboard Navigation Guide")
nav_c1, nav_c2, nav_c3 = st.columns(3)

with nav_c1:
    st.markdown(f"""
    <div style="background-color: {COLOR_CARD_BG}; padding: 16px; border-radius: 8px; border: 1px solid #334155;">
        <h4 style="color: #38BDF8; margin-top: 0;">1. Overview & Landscape</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            High-level distribution of pressure across 200,999 balls, macro benchmarks, and side-by-side leaderboards.
        </p>
    </div>
    """, unsafe_allow_html=True)

with nav_c2:
    st.markdown(f"""
    <div style="background-color: {COLOR_CARD_BG}; padding: 16px; border-radius: 8px; border: 1px solid #334155;">
        <h4 style="color: {COLOR_BATTING}; margin-top: 0;">2 & 3. Discipline Analytics</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            Deep-dive into Batting and Bowling leaderboards with interactive filtering, clutch lift charts, and quadrant scatters.
        </p>
    </div>
    """, unsafe_allow_html=True)

with nav_c3:
    st.markdown(f"""
    <div style="background-color: {COLOR_CARD_BG}; padding: 16px; border-radius: 8px; border: 1px solid #334155;">
        <h4 style="color: #F59E0B; margin-top: 0;">4 & 5. Explorer & Profiles</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            Inspect delivery-level pressure progressions for iconic matches and view comprehensive scouting profiles.
        </p>
    </div>
    """, unsafe_allow_html=True)
