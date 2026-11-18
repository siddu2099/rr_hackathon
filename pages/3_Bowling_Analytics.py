"""
Page 3: Bowling Analytics
Deep-dive into high-pressure run suppression, wicket threat, and economy containment.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from app.config import (
    COLOR_BOWLING,
    COLOR_CARD_BG,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_EMERALD,
    BOWLER_MIN_BALLS
)
from app.components import (
    render_header,
    render_kpi,
    render_player_summary_card,
    render_sidebar_footer,
    apply_custom_css
)
from app.data_loader import (
    load_top10_bowlers,
    load_bowling_rankings
)
from app.analytics import (
    filter_bowling_leaderboard,
    get_bowler_profile
)
from app.charts import (
    create_bpri_ranking_chart,
    create_econ_comparison_scatter,
    create_boundary_dot_scatter
)

apply_custom_css()
render_sidebar_footer()

render_header(
    title="Bowling Analytics: High-Pressure Run Suppression",
    subtitle="Evaluating 133 qualified bowlers across containment, wicket generation, clutch suppression, and volume.",
    badge="Bowling Model 1 (Balanced)"
)

# Load canonical data
df_top10 = load_top10_bowlers()
df_full = load_bowling_rankings()

# Sidebar Interactive Filters
st.sidebar.header("🔍 Bowling Filters")

view_mode = st.sidebar.radio("Leaderboard View", ["Top 10 Official Leaderboard", "All Qualified Bowlers (133 Pool)"])

min_balls = st.sidebar.slider(
    "Minimum Pressure Legal Balls",
    min_value=20,
    max_value=250,
    value=BOWLER_MIN_BALLS,
    step=5,
    help="Default threshold is 60 pressure legal deliveries."
)

bpri_range = st.sidebar.slider(
    "BPRI Score Range",
    min_value=50.0,
    max_value=100.0,
    value=(70.0, 100.0),
    step=0.5
)

econ_range = st.sidebar.slider(
    "Pressure Economy Range",
    min_value=3.0,
    max_value=13.0,
    value=(3.0, 10.0),
    step=0.25
)

min_wickets = st.sidebar.slider(
    "Minimum Pressure Wickets",
    min_value=0,
    max_value=35,
    value=0,
    step=1
)

all_names = sorted(df_full['bowler_name'].unique().tolist())
selected_players = st.sidebar.multiselect(
    "Filter Specific Bowlers",
    options=all_names,
    default=[]
)

# Apply filters
source_df = df_top10 if view_mode == "Top 10 Official Leaderboard" else df_full
filtered_df = filter_bowling_leaderboard(
    source_df,
    min_legal_balls=min_balls,
    bpri_range=bpri_range,
    econ_range=econ_range,
    min_wickets=min_wickets,
    selected_players=selected_players
)

# Top Summary Row for Filtered Selection
s1, s2, s3, s4 = st.columns(4)
with s1:
    render_kpi("Showing Bowlers", f"{len(filtered_df)}", f"Pool: {len(source_df)}", border_accent=COLOR_BOWLING)
with s2:
    mean_bpri = filtered_df['BPRI_Model1_Balanced'].mean() if not filtered_df.empty else 0.0
    render_kpi("Mean BPRI Score", f"{mean_bpri:.2f}", "Across selected group", border_accent=COLOR_BOWLING)
with s3:
    mean_econ = filtered_df['p_economy'].mean() if not filtered_df.empty else 0.0
    render_kpi("Mean Pressure Economy", f"{mean_econ:.2f}", "Tournament Par: 8.33", border_accent=COLOR_BOWLING)
with s4:
    mean_supp = filtered_df['unbiased_delta_econ'].mean() if not filtered_df.empty else 0.0
    render_kpi("Mean Run Suppression", f"{mean_supp:.2f} RPO", "ΔEcon = Non-P Econ - P Econ", border_accent=COLOR_EMERALD)

st.markdown("---")

# Main Leaderboard Table
st.markdown("### 📋 Bowling Pressure Leaderboard")
st.caption("ℹ️ **Sign Convention:** `Delta Econ = Non-pressure economy - Pressure economy`. Positive values indicate superior run suppression under pressure.")

display_cols = [
    'rank', 'bowler_name', 'BPRI_Model1_Balanced', 'p_legal_balls', 
    'p_overs', 'p_runs_conceded', 'p_economy', 'np_economy', 
    'unbiased_delta_econ', 'p_wickets', 'p_bowl_sr', 'p_dot_pct', 'p_boundary_pct'
]
cols_rename = {
    'rank': 'Rank',
    'bowler_name': 'Bowler Name',
    'BPRI_Model1_Balanced': 'BPRI Score',
    'p_legal_balls': 'Legal Balls',
    'p_overs': 'Overs',
    'p_runs_conceded': 'Runs Conceded',
    'p_economy': 'Pressure Econ',
    'np_economy': 'Non-Pressure Econ',
    'unbiased_delta_econ': 'Suppression (ΔEcon)',
    'p_wickets': 'Wickets',
    'p_bowl_sr': 'Strike Rate',
    'p_dot_pct': 'Dot %',
    'p_boundary_pct': 'Boundary %'
}

valid_cols = [c for c in display_cols if c in filtered_df.columns]
tbl = filtered_df[valid_cols].rename(columns=cols_rename)

format_dict = {
    'BPRI Score': '{:.2f}',
    'Overs': '{:.1f}',
    'Pressure Econ': '{:.2f}',
    'Non-Pressure Econ': '{:.2f}',
    'Suppression (ΔEcon)': '{:.2f}',
    'Strike Rate': '{:.1f}',
    'Dot %': '{:.1f}%',
    'Boundary %': '{:.1f}%'
}

st.dataframe(
    tbl.style.format(format_dict, na_rep="N/A"),
    use_container_width=True,
    hide_index=True
)

# Download CSV button
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Bowling CSV",
    data=csv_data,
    file_name="superr_selector_bowling_filtered.csv",
    mime="text/csv"
)

st.markdown("---")

# Visualizations Row 1: BPRI Ranking & Economy Comparison Scatter
st.markdown("### 📊 Interactive Visualizations")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig_bpri = create_bpri_ranking_chart(filtered_df, discipline="bowling")
    st.plotly_chart(fig_bpri, use_container_width=True)

with col_chart2:
    fig_econ = create_econ_comparison_scatter(filtered_df)
    st.plotly_chart(fig_econ, use_container_width=True)

# Visualizations Row 2: Boundary vs Dot Scatter & Delta Econ Bar
col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    fig_bdry = create_boundary_dot_scatter(filtered_df, discipline="bowling")
    st.plotly_chart(fig_bdry, use_container_width=True)

with col_chart4:
    # Delta Econ bar chart for Top 10
    fig_delta = px.bar(
        filtered_df.sort_values(by='unbiased_delta_econ', ascending=True).tail(10),
        x='unbiased_delta_econ',
        y='bowler_name',
        orientation='h',
        color='unbiased_delta_econ',
        color_continuous_scale='Blues',
        labels={'unbiased_delta_econ': 'Clutch Suppression: ΔEcon (RPO saved under pressure)', 'bowler_name': 'Bowler'},
        title="<b>Run Suppression: Unbiased ΔEcon Leaderboard</b>"
    )
    fig_delta.update_layout(paper_bgcolor=COLOR_CARD_BG, plot_bgcolor=COLOR_CARD_BG, font=dict(color=COLOR_TEXT_PRIMARY))
    st.plotly_chart(fig_delta, use_container_width=True)

st.markdown("---")

# Section: Selected Bowler Deep-Dive
st.markdown("### 🔍 Bowler Profile Deep-Dive")
selected_name = st.selectbox(
    "Select a bowler to inspect comprehensive metrics:",
    options=all_names,
    index=all_names.index("Abrar Ahmed") if "Abrar Ahmed" in all_names else 0
)

profile = get_bowler_profile(selected_name)
if profile:
    render_player_summary_card(profile, role="bowler")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        render_kpi("Pressure Legal Balls", f"{profile['p_legal_balls']}", f"{profile['p_overs']:.1f} Overs ({profile['p_matches']} Matches)", border_accent=COLOR_BOWLING)
    with m2:
        render_kpi("Pressure Wickets", f"{profile['p_wickets']}", f"SR: {profile['p_bowl_sr']:.1f} balls/wkt", border_accent=COLOR_BOWLING)
    with m3:
        render_kpi("Pressure Economy", f"{profile['p_economy']:.2f}", f"EB Shrunk: {profile['eb_p_econ']:.2f}", border_accent=COLOR_BOWLING)
    with m4:
        np_econ_str = f"{profile['np_economy']:.2f}" if profile['np_economy'] else "N/A"
        render_kpi("Non-Pressure Econ", np_econ_str, "P < 45 Deliveries", border_accent=COLOR_TEXT_MUTED)
    with m5:
        delta_str = f"{profile['unbiased_delta_econ']:.2f}" if profile['unbiased_delta_econ'] else "N/A"
        render_kpi("Suppression (ΔEcon)", delta_str, "RPO Saved", border_accent=COLOR_EMERALD)

    m6, m7, m8, m9 = st.columns(4)
    with m6:
        render_kpi("Dot Ball %", f"{profile['p_dot_pct']:.1f}%", "Pressure Scoreless Balls")
    with m7:
        render_kpi("Boundary % Conceded", f"{profile['p_boundary_pct']:.1f}%", "Fours & Sixes Allowed")
    with m8:
        render_kpi("Consistency", f"{profile['consistency_pct']:.1f}%", "Spells with Econ <= 8.50")
    with m9:
        render_kpi("BPRI Model Rank", f"#{profile['rank']}", f"Score: {profile['bpri']:.2f}")
