"""
Page 4: Pressure Explorer
Interactive situational analysis of match pressure progression across overs, innings, and deliveries.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from app.config import (
    COLOR_BATTING,
    COLOR_BOWLING,
    COLOR_CARD_BG,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    PRESSURE_THRESHOLD
)
from app.components import (
    render_header,
    render_kpi,
    render_sidebar_footer,
    apply_custom_css
)
from app.data_loader import load_deliveries_pressure
from app.charts import create_pressure_progression_chart

apply_custom_css()
render_sidebar_footer()

render_header(
    title="Pressure Explorer: Match Situations & Leverage",
    subtitle="Inspect situational pressure dynamics, over-by-over leverage, and iconic forensic match timelines.",
    badge="Delivery-Level Exploration"
)

# Load full delivery dataset with cached projection
with st.spinner("Loading delivery-level pressure database (200,999 records)..."):
    df_deliv = load_deliveries_pressure()

# Sidebar Filters
st.sidebar.header("🔍 Situational Filters")

comp_cats = sorted([str(c) for c in df_deliv['comp_category'].unique() if pd.notna(c)])
selected_comps = st.sidebar.multiselect(
    "Competition Category",
    options=comp_cats,
    default=comp_cats
)

tier_options = ['Low', 'Moderate', 'High', 'Critical']
selected_tiers = st.sidebar.multiselect(
    "Pressure Tier",
    options=tier_options,
    default=tier_options
)

p_range = st.sidebar.slider(
    "Continuous Pressure Score (P)",
    min_value=0.0,
    max_value=100.0,
    value=(0.0, 100.0),
    step=1.0
)

innings_choice = st.sidebar.selectbox("Innings", ["All Innings", "1st Innings (Setting)", "2nd Innings (Chasing)"])

over_range = st.sidebar.slider(
    "Over Number",
    min_value=1,
    max_value=20,
    value=(1, 20),
    step=1
)

# Apply filters efficiently
filtered = df_deliv[
    (df_deliv['comp_category'].astype(str).isin(selected_comps)) &
    (df_deliv['pressure_tier'].astype(str).isin(selected_tiers)) &
    (df_deliv['pressure_score'] >= p_range[0]) &
    (df_deliv['pressure_score'] <= p_range[1]) &
    (df_deliv['overid'] >= over_range[0]) &
    (df_deliv['overid'] <= over_range[1])
]

if innings_choice == "1st Innings (Setting)":
    filtered = filtered[filtered['innings'] == 1]
elif innings_choice == "2nd Innings (Chasing)":
    filtered = filtered[filtered['innings'] == 2]

# Summary KPI Cards for Selection
s1, s2, s3, s4 = st.columns(4)
with s1:
    render_kpi("Filtered Deliveries", f"{len(filtered):,}", f"{len(filtered)/len(df_deliv)*100:.1f}% of total", border_accent=COLOR_BOWLING)
with s2:
    mean_p = filtered['pressure_score'].mean() if not filtered.empty else 0.0
    render_kpi("Mean Pressure Score", f"{mean_p:.1f}", "P in [0, 100]", border_accent=COLOR_BATTING)
with s3:
    n_high = (filtered['pressure_score'] >= PRESSURE_THRESHOLD).sum()
    render_kpi("High Pressure Balls", f"{n_high:,}", f"P >= {PRESSURE_THRESHOLD}", border_accent=COLOR_BATTING)
with s4:
    n_wkts = filtered['is_wicket'].sum()
    render_kpi("Wickets in Slice", f"{n_wkts:,}", f"{filtered['runs'].sum():,} Runs Conceded", border_accent=COLOR_BOWLING)

st.markdown("---")

# Feature 1: Forensic Case Study Timelines
st.markdown("### 🎯 Iconic Forensic Match Case Studies")
st.markdown("Select a verified match to visualize how pressure evolved ball-by-ball across the chase or death defense:")

case_studies = {
    "Match 20193: Rinku Singh 5-Six Finish (KKR vs GT, IPL 2023)": (20193, 2, "KKR Chase: Rinku Singh 48* (Match 20193)"),
    "Match 31250: Jos Buttler Record Century Chase (RR vs KKR, IPL 2024)": (31250, 2, "RR Chase: Jos Buttler 107* (Match 31250)"),
    "Match 20222: Tim David 45* Death Heroics (MI vs RR, IPL 2023)": (20222, 2, "MI Chase: Tim David 45* (Match 20222)"),
    "Match 31227: Abrar Ahmed Choking Death Overs (PAK vs AUS, 2024)": (31227, 2, "Death Defense: Abrar Ahmed (Match 31227)"),
    "Match 20235: Kuldeep Yadav Middle-Overs Choke (DC vs LSG, IPL 2024)": (20235, 2, "Middle-Overs Choke: Kuldeep Yadav (Match 20235)")
}

selected_case = st.selectbox("Select Match Scenario:", list(case_studies.keys()))
m_id, m_inn, m_title = case_studies[selected_case]

match_data = df_deliv[(df_deliv['match_id'] == m_id) & (df_deliv['innings'] == m_inn)].sort_values(by=['overid', 'over_ball_num'])

if not match_data.empty:
    fig_timeline = create_pressure_progression_chart(match_data, match_title=m_title)
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Case study summary callout
    p_balls_case = match_data[match_data['pressure_score'] >= PRESSURE_THRESHOLD]
    st.caption(rf"📌 **Match Summary:** {len(match_data)} total balls in innings. {len(p_balls_case)} balls ({len(p_balls_case)/len(match_data)*100:.1f}%) crossed the high-pressure threshold ($P \ge 45.0$).")
else:
    st.info("Delivery records for selected match are not in the current slice.")

st.markdown("---")

# Feature 2: Pressure by Over Analysis
st.markdown("### 📈 Average Match Pressure Across Overs (1 to 20)")
col_ov1, col_ov2 = st.columns(2)

with col_ov1:
    over_agg = df_deliv.groupby(['overid', 'innings'], observed=True)['pressure_score'].mean().reset_index()
    over_agg['innings_label'] = over_agg['innings'].map({1: '1st Innings (Setting)', 2: '2nd Innings (Chasing)'})
    over_agg = over_agg.dropna(subset=['innings_label'])
    
    fig_over = px.line(
        over_agg,
        x='overid',
        y='pressure_score',
        color='innings_label',
        color_discrete_map={'1st Innings (Setting)': COLOR_BOWLING, '2nd Innings (Chasing)': COLOR_BATTING},
        markers=True,
        labels={'overid': 'Over Number', 'pressure_score': 'Mean Pressure (P)', 'innings_label': 'Innings'},
        title="<b>Mean Pressure Progression: 1st vs 2nd Innings</b>"
    )
    fig_over.add_hline(y=PRESSURE_THRESHOLD, line_dash='dash', line_color='#F59E0B', annotation_text="P = 45 Cutoff")
    fig_over.update_layout(paper_bgcolor=COLOR_CARD_BG, plot_bgcolor=COLOR_CARD_BG, font=dict(color=COLOR_TEXT_PRIMARY))
    st.plotly_chart(fig_over, use_container_width=True)

with col_ov2:
    tier_counts = filtered['pressure_tier'].value_counts().reset_index()
    tier_counts.columns = ['Tier', 'Deliveries']
    
    fig_tier = px.pie(
        tier_counts,
        names='Tier',
        values='Deliveries',
        color='Tier',
        color_discrete_map={
            'Low': '#64748B',
            'Moderate': '#38BDF8',
            'High': '#F59E0B',
            'Critical': '#BE123C'
        },
        hole=0.45,
        title="<b>Pressure Tier Breakdown in Filtered Slice</b>"
    )
    fig_tier.update_layout(paper_bgcolor=COLOR_CARD_BG, plot_bgcolor=COLOR_CARD_BG, font=dict(color=COLOR_TEXT_PRIMARY))
    st.plotly_chart(fig_tier, use_container_width=True)

st.markdown("---")

# Feature 3: Delivery-Level Data Table Inspection
st.markdown("### 📑 Delivery-Level Event Log")
st.markdown("Previewing the top 100 deliveries matching active filters:")

table_cols = [
    'match_id', 'innings', 'overid', 'over_ball_num', 'striker_name', 
    'bowler_name', 'runs', 'is_four', 'is_six', 'is_wicket', 
    'pressure_score', 'pressure_tier'
]
disp_deliv = filtered[table_cols].head(100).copy()
disp_deliv.columns = [
    'Match ID', 'Inn', 'Over', 'Ball', 'Striker', 
    'Bowler', 'Runs', '4s', '6s', 'Wkt', 
    'Pressure (P)', 'Tier'
]

st.dataframe(
    disp_deliv.style.format({
        'Pressure (P)': '{:.1f}'
    }),
    use_container_width=True,
    hide_index=True
)

st.download_button(
    label="📥 Download Filtered Deliveries CSV (Sample)",
    data=disp_deliv.to_csv(index=False).encode('utf-8'),
    file_name="superr_selector_deliveries_sample.csv",
    mime="text/csv"
)
