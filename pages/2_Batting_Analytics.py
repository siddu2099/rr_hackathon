"""
Page 2: Batting Analytics
Deep-dive into high-pressure batting execution, clutch lift, and consistency.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from app.config import (
    COLOR_BATTING,
    COLOR_CARD_BG,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_EMERALD,
    BATTER_MIN_BALLS
)
from app.components import (
    render_header,
    render_kpi,
    render_player_summary_card,
    render_sidebar_footer,
    apply_custom_css
)
from app.data_loader import (
    load_top10_batters,
    load_batting_rankings
)
from app.analytics import (
    filter_batting_leaderboard,
    get_batter_profile
)
from app.charts import (
    create_bpri_ranking_chart,
    create_sr_comparison_scatter,
    create_boundary_dot_scatter
)

apply_custom_css()
render_sidebar_footer()

render_header(
    title="Batting Analytics: High-Pressure Value Generation",
    subtitle="Evaluating 153 qualified batters across execution, clutch lift, consistency, and sample volume.",
    badge="Batting Model 1 (Balanced)"
)

# Load canonical data
df_top10 = load_top10_batters()
df_full = load_batting_rankings()

# Sidebar Interactive Filters
st.sidebar.header("🔍 Batting Filters")

view_mode = st.sidebar.radio("Leaderboard View", ["Top 10 Official Leaderboard", "All Qualified Batters (153 Pool)"])

min_balls = st.sidebar.slider(
    "Minimum Pressure Balls Faced",
    min_value=20,
    max_value=200,
    value=BATTER_MIN_BALLS,
    step=5,
    help="Default threshold is 50 pressure balls faced."
)

bpri_range = st.sidebar.slider(
    "BPRI Score Range",
    min_value=50.0,
    max_value=100.0,
    value=(70.0, 100.0),
    step=0.5
)

sr_range = st.sidebar.slider(
    "Pressure Strike Rate Range",
    min_value=100.0,
    max_value=250.0,
    value=(120.0, 240.0),
    step=5.0
)

all_names = sorted(df_full['striker_name'].unique().tolist())
selected_players = st.sidebar.multiselect(
    "Filter Specific Players",
    options=all_names,
    default=[]
)

# Apply filters
source_df = df_top10 if view_mode == "Top 10 Official Leaderboard" else df_full
filtered_df = filter_batting_leaderboard(
    source_df,
    min_balls=min_balls,
    bpri_range=bpri_range,
    sr_range=sr_range,
    selected_players=selected_players
)

# Top Summary Row for Filtered Selection
s1, s2, s3, s4 = st.columns(4)
with s1:
    render_kpi("Showing Batters", f"{len(filtered_df)}", f"Pool: {len(source_df)}", border_accent=COLOR_BATTING)
with s2:
    mean_bpri = filtered_df['BPRI_Model1_Balanced'].mean() if not filtered_df.empty else 0.0
    render_kpi("Mean BPRI Score", f"{mean_bpri:.2f}", "Across selected group", border_accent=COLOR_BATTING)
with s3:
    mean_sr = filtered_df['p_strike_rate'].mean() if not filtered_df.empty else 0.0
    render_kpi("Mean Pressure SR", f"{mean_sr:.1f}", "Tournament Par: 136.1", border_accent=COLOR_BATTING)
with s4:
    mean_lift = filtered_df['unbiased_delta_sr'].mean() if not filtered_df.empty else 0.0
    render_kpi("Mean Clutch Lift", f"+{mean_lift:.1f}" if mean_lift > 0 else f"{mean_lift:.1f}", "vs Non-Pressure Baseline", border_accent=COLOR_EMERALD)

st.markdown("---")

# Main Leaderboard Table
st.markdown("### 📋 Batting Pressure Leaderboard")

display_cols = [
    'rank', 'striker_name', 'BPRI_Model1_Balanced', 'p_balls_faced', 
    'p_runs', 'p_strike_rate', 'np_bat_sr', 'unbiased_delta_sr', 
    'p_boundary_pct', 'p_dot_pct', 'pct_matches_above_140'
]
cols_rename = {
    'rank': 'Rank',
    'striker_name': 'Batter Name',
    'BPRI_Model1_Balanced': 'BPRI Score',
    'p_balls_faced': 'Pressure BF',
    'p_runs': 'Runs',
    'p_strike_rate': 'Pressure SR',
    'np_bat_sr': 'Non-Pressure SR',
    'unbiased_delta_sr': 'Clutch Lift (ΔSR)',
    'p_boundary_pct': 'Boundary %',
    'p_dot_pct': 'Dot %',
    'pct_matches_above_140': 'Consistency (%)'
}

valid_cols = [c for c in display_cols if c in filtered_df.columns]
tbl = filtered_df[valid_cols].rename(columns=cols_rename)

format_dict = {
    'BPRI Score': '{:.2f}',
    'Pressure SR': '{:.1f}',
    'Non-Pressure SR': '{:.1f}',
    'Clutch Lift (ΔSR)': '+{:.1f}',
    'Boundary %': '{:.1f}%',
    'Dot %': '{:.1f}%',
    'Consistency (%)': '{:.1f}%'
}

st.dataframe(
    tbl.style.format(format_dict, na_rep="N/A"),
    use_container_width=True,
    hide_index=True
)

# Download CSV button
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Batting CSV",
    data=csv_data,
    file_name="superr_selector_batting_filtered.csv",
    mime="text/csv"
)

st.markdown("---")

# Visualizations Row 1: BPRI Ranking & Clutch Lift Scatter
st.markdown("### 📊 Interactive Visualizations")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig_bpri = create_bpri_ranking_chart(filtered_df, discipline="batting")
    st.plotly_chart(fig_bpri, use_container_width=True)

with col_chart2:
    fig_sr = create_sr_comparison_scatter(filtered_df)
    st.plotly_chart(fig_sr, use_container_width=True)

# Visualizations Row 2: Boundary vs Dot Scatter & Delta SR
col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    fig_bdry = create_boundary_dot_scatter(filtered_df, discipline="batting")
    st.plotly_chart(fig_bdry, use_container_width=True)

with col_chart4:
    # Delta SR bar chart for Top 10
    fig_delta = px.bar(
        filtered_df.sort_values(by='unbiased_delta_sr', ascending=True).tail(10),
        x='unbiased_delta_sr',
        y='striker_name',
        orientation='h',
        color='unbiased_delta_sr',
        color_continuous_scale='Reds',
        labels={'unbiased_delta_sr': 'Clutch Lift: ΔSR (Pressure vs Non-Pressure)', 'striker_name': 'Batter'},
        title="<b>Clutch Acceleration: Unbiased ΔSR Leaderboard</b>"
    )
    fig_delta.update_layout(paper_bgcolor=COLOR_CARD_BG, plot_bgcolor=COLOR_CARD_BG, font=dict(color=COLOR_TEXT_PRIMARY))
    st.plotly_chart(fig_delta, use_container_width=True)

st.markdown("---")

# Section: Selected Player Deep-Dive
st.markdown("### 🔍 Batter Profile Deep-Dive")
selected_name = st.selectbox(
    "Select a batter to inspect comprehensive metrics:",
    options=all_names,
    index=all_names.index("Rinku Singh") if "Rinku Singh" in all_names else 0
)

profile = get_batter_profile(selected_name)
if profile:
    render_player_summary_card(profile, role="batter")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        render_kpi("Pressure Balls", f"{profile['p_balls_faced']}", f"Across {profile['p_matches']} Matches", border_accent=COLOR_BATTING)
    with m2:
        render_kpi("Pressure Runs", f"{profile['p_runs']}", f"Dismissals: {profile.get('p_dismissal_rate', 0):.2f}/ball", border_accent=COLOR_BATTING)
    with m3:
        render_kpi("Pressure Strike Rate", f"{profile['p_strike_rate']:.1f}", f"EB Shrunk: {profile['eb_p_sr']:.1f}", border_accent=COLOR_BATTING)
    with m4:
        np_sr_str = f"{profile['np_bat_sr']:.1f}" if profile['np_bat_sr'] else "N/A"
        render_kpi("Non-Pressure SR", np_sr_str, "P < 45 Deliveries", border_accent=COLOR_TEXT_MUTED)
    with m5:
        delta_str = f"+{profile['unbiased_delta_sr']:.1f}" if profile['unbiased_delta_sr'] else "N/A"
        render_kpi("Clutch Lift (ΔSR)", delta_str, "Pressure Margin", border_accent=COLOR_EMERALD)

    m6, m7, m8, m9 = st.columns(4)
    with m6:
        render_kpi("Boundary %", f"{profile['p_boundary_pct']:.1f}%", "Fours & Sixes Under Pressure")
    with m7:
        render_kpi("Dot Ball %", f"{profile['p_dot_pct']:.1f}%", "Scoreless Deliveries")
    with m8:
        render_kpi("Consistency", f"{profile['consistency_pct']:.1f}%", "Innings with SR >= 140")
    with m9:
        render_kpi("BPRI Model Rank", f"#{profile['rank']}", f"Score: {profile['bpri']:.2f}")
