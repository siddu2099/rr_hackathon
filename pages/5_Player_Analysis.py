"""
Page 5: Player Analysis & Scouting Profile
Comprehensive multi-condition evaluation comparing high-pressure vs non-pressure performance.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.config import (
    COLOR_BATTING,
    COLOR_BOWLING,
    COLOR_CARD_BG,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_EMERALD,
    BAT_PRIOR_MU,
    BOWL_PRIOR_MU
)
from app.components import (
    render_header,
    render_kpi,
    render_player_summary_card,
    render_sidebar_footer,
    apply_custom_css
)
from app.data_loader import (
    load_batting_rankings,
    load_bowling_rankings,
    load_deliveries_pressure
)
from app.analytics import (
    get_batter_profile,
    get_bowler_profile,
    get_player_match_breakdown
)

apply_custom_css()
render_sidebar_footer()

render_header(
    title="Player Analysis: Individual Scouting & Clutch Profiles",
    subtitle="Side-by-side contrast of high-pressure execution versus non-pressure career baselines.",
    badge="Player Intelligence"
)

# Role Selector
role_choice = st.radio("Select Discipline", ["Batting", "Bowling"], horizontal=True)

df_bat_rank = load_batting_rankings()
df_bowl_rank = load_bowling_rankings()

if role_choice == "Batting":
    all_players = sorted(df_bat_rank['striker_name'].unique().tolist())
    default_idx = all_players.index("Rinku Singh") if "Rinku Singh" in all_players else 0
    selected_player = st.selectbox("Select Batter to Scout:", all_players, index=default_idx)
    profile = get_batter_profile(selected_player)
    
    if profile:
        render_player_summary_card(profile, role="batter")
        
        # Section 1: Tri-Condition Comparison Cards
        st.markdown("### 📊 Performance Across Pressure Regimes")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown(f"<div style='background-color: {COLOR_CARD_BG}; padding: 15px; border-radius: 8px; border: 1px solid #334155;'>"
                        f"<h4 style='color: #64748B; margin: 0;'>Low / Non-Pressure (P < 45)</h4>"
                        f"<p style='font-size: 1.8rem; font-weight: 800; color: #F8FAFC; margin: 8px 0;'>"
                        f"{profile['np_bat_sr']:.1f} SR" if profile['np_bat_sr'] else "N/A"
                        f"</p><div style='font-size: 0.85rem; color: #94A3B8;'>Standard match conditions</div></div>", unsafe_allow_html=True)
                        
        with c2:
            st.markdown(f"<div style='background-color: {COLOR_CARD_BG}; padding: 15px; border-radius: 8px; border: 1px solid {COLOR_BATTING};'>"
                        f"<h4 style='color: {COLOR_BATTING}; margin: 0;'>High Pressure (P >= 45)</h4>"
                        f"<p style='font-size: 1.8rem; font-weight: 800; color: #F8FAFC; margin: 8px 0;'>"
                        f"{profile['p_strike_rate']:.1f} SR"
                        f"</p><div style='font-size: 0.85rem; color: #94A3B8;'>{profile['p_balls_faced']} Balls • {profile['p_runs']} Runs</div></div>", unsafe_allow_html=True)
                        
        with c3:
            delta_val = profile['unbiased_delta_sr']
            delta_str = f"+{delta_val:.1f}" if delta_val and delta_val > 0 else (f"{delta_val:.1f}" if delta_val else "N/A")
            delta_color = COLOR_EMERALD if delta_val and delta_val > 0 else COLOR_BATTING
            st.markdown(f"<div style='background-color: {COLOR_CARD_BG}; padding: 15px; border-radius: 8px; border: 1px solid #334155;'>"
                        f"<h4 style='color: {delta_color}; margin: 0;'>Clutch Lift (ΔSR)</h4>"
                        f"<p style='font-size: 1.8rem; font-weight: 800; color: {delta_color}; margin: 8px 0;'>"
                        f"{delta_str}"
                        f"</p><div style='font-size: 0.85rem; color: #94A3B8;'>SR Acceleration Margin</div></div>", unsafe_allow_html=True)

        st.markdown("---")

        # Section 2: Detailed Rate Metrics & BPRI Breakdown
        st.markdown("### 🧩 Component Breakdown & Rate Metrics")
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            render_kpi("Empirical Bayes SR", f"{profile['eb_p_sr']:.1f}", f"Tournament Prior: {BAT_PRIOR_MU:.1f}")
        with b2:
            render_kpi("Boundary %", f"{profile['p_boundary_pct']:.1f}%", "Fours & Sixes Under Pressure")
        with b3:
            render_kpi("Dot Ball %", f"{profile['p_dot_pct']:.1f}%", "Avoidance of Wasted Deliveries")
        with b4:
            render_kpi("Consistency %", f"{profile['consistency_pct']:.1f}%", "% Innings Achieving SR >= 140")

        # Tier progression chart if available
        tiers = ['Low (<20)', 'Moderate (20-45)', 'High (45-70)', 'Critical (>=70)']
        tier_srs = [profile['low_sr'], profile['moderate_sr'], profile['high_sr'], profile['critical_sr']]
        
        valid_tier_data = [(t, s) for t, s in zip(tiers, tier_srs) if pd.notna(s)]
        if len(valid_tier_data) >= 2:
            st.markdown("#### 📈 Strike Rate Across Pressure Tiers")
            df_tier = pd.DataFrame(valid_tier_data, columns=['Tier', 'Strike Rate'])
            fig_tier = px.bar(
                df_tier,
                x='Tier',
                y='Strike Rate',
                color='Strike Rate',
                color_continuous_scale='Reds',
                title=f"<b>{profile['name']}: Strike Rate by Pressure Tier</b>"
            )
            fig_tier.add_hline(y=BAT_PRIOR_MU, line_dash="dash", line_color="#94A3B8", annotation_text="Par (136.1)")
            fig_tier.update_layout(paper_bgcolor=COLOR_CARD_BG, plot_bgcolor=COLOR_CARD_BG, font=dict(color=COLOR_TEXT_PRIMARY))
            st.plotly_chart(fig_tier, use_container_width=True)

        st.markdown("---")

        # Section 3: Match-by-Match Pressure Performance Log
        st.markdown(f"### 📋 Match-Level Pressure Logs for {profile['name']}")
        with st.spinner("Extracting match innings logs..."):
            df_deliv = load_deliveries_pressure(pressure_only=True)
            match_logs = get_player_match_breakdown(profile['player_id'], role='batter', df_deliv=df_deliv)
            
        if not match_logs.empty:
            match_logs.columns = ['Match ID', 'Innings', 'Season', 'Competition', 'Pressure BF', 'Runs', '4s', '6s', 'Mean Pressure', 'Strike Rate']
            st.dataframe(
                match_logs.style.format({
                    'Mean Pressure': '{:.1f}',
                    'Strike Rate': '{:.1f}'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No delivery logs found for this player in pressure conditions.")

else:  # Bowling Profile
    all_bowlers = sorted(df_bowl_rank['bowler_name'].unique().tolist())
    default_idx = all_bowlers.index("Abrar Ahmed") if "Abrar Ahmed" in all_bowlers else 0
    selected_player = st.selectbox("Select Bowler to Scout:", all_bowlers, index=default_idx)
    profile = get_bowler_profile(selected_player)
    
    if profile:
        render_player_summary_card(profile, role="bowler")
        
        # Section 1: Tri-Condition Comparison Cards
        st.markdown("### 📊 Performance Across Pressure Regimes")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown(f"<div style='background-color: {COLOR_CARD_BG}; padding: 15px; border-radius: 8px; border: 1px solid #334155;'>"
                        f"<h4 style='color: #64748B; margin: 0;'>Low / Non-Pressure (P < 45)</h4>"
                        f"<p style='font-size: 1.8rem; font-weight: 800; color: #F8FAFC; margin: 8px 0;'>"
                        f"{profile['np_economy']:.2f} Econ" if profile['np_economy'] else "N/A"
                        f"</p><div style='font-size: 0.85rem; color: #94A3B8;'>Standard match conditions</div></div>", unsafe_allow_html=True)
                        
        with c2:
            st.markdown(f"<div style='background-color: {COLOR_CARD_BG}; padding: 15px; border-radius: 8px; border: 1px solid {COLOR_BOWLING};'>"
                        f"<h4 style='color: {COLOR_BOWLING}; margin: 0;'>High Pressure (P >= 45)</h4>"
                        f"<p style='font-size: 1.8rem; font-weight: 800; color: #F8FAFC; margin: 8px 0;'>"
                        f"{profile['p_economy']:.2f} Econ"
                        f"</p><div style='font-size: 0.85rem; color: #94A3B8;'>{profile['p_legal_balls']} Balls • {profile['p_wickets']} Wickets</div></div>", unsafe_allow_html=True)
                        
        with c3:
            delta_val = profile['unbiased_delta_econ']
            delta_str = f"{delta_val:.2f} RPO" if delta_val else "N/A"
            delta_color = COLOR_EMERALD if delta_val and delta_val > 0 else COLOR_BATTING
            st.markdown(f"<div style='background-color: {COLOR_CARD_BG}; padding: 15px; border-radius: 8px; border: 1px solid #334155;'>"
                        f"<h4 style='color: {delta_color}; margin: 0;'>Clutch Suppression (ΔEcon)</h4>"
                        f"<p style='font-size: 1.8rem; font-weight: 800; color: {delta_color}; margin: 8px 0;'>"
                        f"{delta_str}"
                        f"</p><div style='font-size: 0.85rem; color: #94A3B8;'>Runs Saved vs Baseline</div></div>", unsafe_allow_html=True)

        st.markdown("---")

        # Section 2: Detailed Rate Metrics & BPRI Breakdown
        st.markdown("### 🧩 Component Breakdown & Rate Metrics")
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            render_kpi("Empirical Bayes Econ", f"{profile['eb_p_econ']:.2f}", f"Tournament Prior: {BOWL_PRIOR_MU:.2f}")
        with b2:
            render_kpi("Dot Ball %", f"{profile['p_dot_pct']:.1f}%", "Pressure Scoreless Deliveries")
        with b3:
            render_kpi("Boundary % Allowed", f"{profile['p_boundary_pct']:.1f}%", "Fours & Sixes Conceded")
        with b4:
            render_kpi("Consistency %", f"{profile['consistency_pct']:.1f}%", "% Spells Conceding <= 8.50 RPO")

        # Tier progression chart if available
        tiers = ['Low (<20)', 'Moderate (20-45)', 'High (45-70)', 'Critical (>=70)']
        tier_econs = [profile['low_econ'], profile['moderate_econ'], profile['high_econ'], profile['critical_econ']]
        
        valid_tier_data = [(t, e) for t, e in zip(tiers, tier_econs) if pd.notna(e)]
        if len(valid_tier_data) >= 2:
            st.markdown("#### 📉 Economy Rate Across Pressure Tiers")
            df_tier = pd.DataFrame(valid_tier_data, columns=['Tier', 'Economy Rate'])
            fig_tier = px.bar(
                df_tier,
                x='Tier',
                y='Economy Rate',
                color='Economy Rate',
                color_continuous_scale='Blues_r',
                title=f"<b>{profile['name']}: Economy Rate by Pressure Tier (Lower is Better)</b>"
            )
            fig_tier.add_hline(y=BOWL_PRIOR_MU, line_dash="dash", line_color="#94A3B8", annotation_text="Par (8.33)")
            fig_tier.update_layout(paper_bgcolor=COLOR_CARD_BG, plot_bgcolor=COLOR_CARD_BG, font=dict(color=COLOR_TEXT_PRIMARY))
            st.plotly_chart(fig_tier, use_container_width=True)

        st.markdown("---")

        # Section 3: Match-by-Match Pressure Performance Log
        st.markdown(f"### 📋 Match-Level Pressure Logs for {profile['name']}")
        with st.spinner("Extracting match spell logs..."):
            df_deliv = load_deliveries_pressure(pressure_only=True)
            match_logs = get_player_match_breakdown(profile['player_id'], role='bowler', df_deliv=df_deliv)
            
        if not match_logs.empty:
            match_logs.columns = ['Match ID', 'Innings', 'Season', 'Competition', 'Legal Balls', 'Runs Conceded', 'Wickets', 'Dots', 'Mean Pressure', 'Economy']
            st.dataframe(
                match_logs.style.format({
                    'Mean Pressure': '{:.1f}',
                    'Economy': '{:.2f}'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No delivery logs found for this bowler in pressure conditions.")
