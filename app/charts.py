"""
Interactive Plotly visualizations for SupeRR Selector Season 2 Dashboard.
Provides publication-quality sports analytics charts with unified dark styling.
"""
from typing import Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from app.config import (
    COLOR_NAVY_BG,
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_BATTING,
    COLOR_BATTING_LIGHT,
    COLOR_BOWLING,
    COLOR_BOWLING_LIGHT,
    COLOR_CRITICAL,
    COLOR_HIGH,
    COLOR_MODERATE,
    COLOR_LOW,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_EMERALD,
    COLOR_AMBER,
    PLOTLY_DARK_LAYOUT,
    PRESSURE_THRESHOLD
)


def apply_theme(fig: go.Figure) -> go.Figure:
    """Apply consistent dark sports-analytics theme to a Plotly figure."""
    fig.update_layout(**PLOTLY_DARK_LAYOUT)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#334155", zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#334155", zeroline=False)
    return fig


def create_pressure_distribution_chart(df_deliv: pd.DataFrame) -> go.Figure:
    """Plot continuous pressure score distribution with tier coloring and cutoff."""
    p_scores = df_deliv['pressure_score'].dropna()
    
    # Create binned distribution
    bins = np.linspace(0, 100, 51)
    hist, bin_edges = np.histogram(p_scores, bins=bins)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    
    # Assign tier colors
    colors = []
    tiers = []
    for b in bin_centers:
        if b < 20:
            colors.append(COLOR_LOW)
            tiers.append("Low (<20)")
        elif b < 45:
            colors.append(COLOR_MODERATE)
            tiers.append("Moderate (20-45)")
        elif b < 70:
            colors.append(COLOR_HIGH)
            tiers.append("High (45-70)")
        else:
            colors.append(COLOR_CRITICAL)
            tiers.append("Critical (>=70)")
            
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=bin_centers,
        y=hist,
        marker=dict(color=colors, line=dict(color="#0F172A", width=0.5)),
        hovertemplate="<b>Pressure Range:</b> %{x:.1f}<br><b>Deliveries:</b> %{y:,}<extra></extra>",
        showlegend=False
    ))
    
    # Threshold indicator
    fig.add_vline(
        x=PRESSURE_THRESHOLD,
        line_width=2.5,
        line_dash="dash",
        line_color=COLOR_BATTING,
        annotation_text="High Pressure Cutoff (P >= 45.0)",
        annotation_position="top right",
        annotation_font=dict(color=COLOR_BATTING_LIGHT, size=11, family="sans-serif")
    )
    
    fig.update_layout(
        title="<b>Distribution of Continuous Match Pressure (P ∈ [0, 100]) Across 200,999 Deliveries</b>",
        xaxis_title="Continuous Pressure Score (P)",
        yaxis_title="Delivery Count",
        height=420
    )
    return apply_theme(fig)


def create_bpri_ranking_chart(df: pd.DataFrame, discipline: str = "batting") -> go.Figure:
    """Create horizontal bar chart of BPRI scores for top performers."""
    df_sorted = df.sort_values(by="BPRI_Model1_Balanced", ascending=True).tail(10)
    
    name_col = "striker_name" if discipline == "batting" else "bowler_name"
    bar_color = COLOR_BATTING if discipline == "batting" else COLOR_BOWLING
    
    hover_tmpl = (
        "<b>%{y}</b><br>"
        "BPRI Score: %{x:.2f}<br>"
        "Pressure SR: %{customdata[0]:.1f}<br>"
        "Unbiased ΔSR: +%{customdata[1]:.1f}<br>"
        "Pressure BF: %{customdata[2]}<extra></extra>"
    ) if discipline == "batting" else (
        "<b>%{y}</b><br>"
        "BPRI Score: %{x:.2f}<br>"
        "Pressure Economy: %{customdata[0]:.2f}<br>"
        "Unbiased ΔEcon: %{customdata[1]:.2f}<br>"
        "Wickets: %{customdata[2]}<extra></extra>"
    )
    
    if discipline == "batting":
        cdata = np.stack((
            df_sorted['p_strike_rate'],
            df_sorted['unbiased_delta_sr'],
            df_sorted['p_balls_faced']
        ), axis=-1)
    else:
        cdata = np.stack((
            df_sorted['p_economy'],
            df_sorted['unbiased_delta_econ'],
            df_sorted['p_wickets']
        ), axis=-1)
        
    fig = go.Figure(go.Bar(
        x=df_sorted['BPRI_Model1_Balanced'],
        y=df_sorted[name_col],
        orientation='h',
        marker=dict(
            color=bar_color,
            line=dict(color="#FDA4AF" if discipline == "batting" else "#7DD3FC", width=1)
        ),
        customdata=cdata,
        hovertemplate=hover_tmpl
    ))
    
    fig.update_layout(
        title=f"<b>Top 10 {discipline.capitalize()} Pressure Leaderboard (BPRI Composite)</b>",
        xaxis_title="BPRI Score",
        yaxis_title="Player",
        xaxis=dict(range=[70, 92]),
        height=450
    )
    return apply_theme(fig)


def create_sr_comparison_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter plot: Pressure Strike Rate vs Non-Pressure Strike Rate."""
    fig = go.Figure()
    
    # 1:1 diagonal line
    max_val = max(df['p_strike_rate'].max(), df['np_bat_sr'].max()) + 15
    min_val = min(df['p_strike_rate'].min(), df['np_bat_sr'].min()) - 15
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        line=dict(color=COLOR_TEXT_MUTED, dash='dash', width=1.5),
        name="Neutral Par (ΔSR = 0)",
        hoverinfo='skip'
    ))
    
    # Scatter points
    fig.add_trace(go.Scatter(
        x=df['np_bat_sr'],
        y=df['p_strike_rate'],
        mode='markers+text',
        text=df['striker_name'],
        textposition="top center",
        marker=dict(
            size=df['p_balls_faced'] / 15.0 + 8,
            color=df['unbiased_delta_sr'],
            colorscale='Turbo',
            colorbar=dict(title="ΔSR (Lift)"),
            showscale=True,
            line=dict(color="#F8FAFC", width=1.2)
        ),
        customdata=np.stack((
            df['unbiased_delta_sr'],
            df['p_balls_faced'],
            df['BPRI_Model1_Balanced']
        ), axis=-1),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Non-Pressure SR: %{x:.1f}<br>"
            "Pressure SR: %{y:.1f}<br>"
            "Clutch Lift (ΔSR): +%{customdata[0]:.1f}<br>"
            "Balls Faced: %{customdata[1]}<br>"
            "BPRI Score: %{customdata[2]:.2f}<extra></extra>"
        ),
        name="Qualified Batters"
    ))
    
    fig.update_layout(
        title="<b>Clutch Lift: Pressure Strike Rate vs. Non-Pressure Baseline</b>",
        xaxis_title="Non-Pressure Strike Rate (P < 45)",
        yaxis_title="Pressure Strike Rate (P >= 45)",
        height=500
    )
    return apply_theme(fig)


def create_econ_comparison_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter plot: Pressure Economy vs Non-Pressure Economy."""
    fig = go.Figure()
    
    max_val = max(df['p_economy'].max(), df['np_economy'].max()) + 1.5
    min_val = min(df['p_economy'].min(), df['np_economy'].min()) - 1.0
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        line=dict(color=COLOR_TEXT_MUTED, dash='dash', width=1.5),
        name="Neutral Par (ΔEcon = 0)",
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['np_economy'],
        y=df['p_economy'],
        mode='markers+text',
        text=df['bowler_name'],
        textposition="top center",
        marker=dict(
            size=df['p_legal_balls'] / 12.0 + 8,
            color=df['unbiased_delta_econ'],
            colorscale='Blues_r',
            colorbar=dict(title="ΔEcon (Suppression)"),
            showscale=True,
            line=dict(color="#F8FAFC", width=1.2)
        ),
        customdata=np.stack((
            df['unbiased_delta_econ'],
            df['p_legal_balls'],
            df['p_wickets'],
            df['BPRI_Model1_Balanced']
        ), axis=-1),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Non-Pressure Econ: %{x:.2f}<br>"
            "Pressure Econ: %{y:.2f}<br>"
            "Clutch Suppression (ΔEcon): %{customdata[0]:.2f}<br>"
            "Legal Balls: %{customdata[1]} | Wickets: %{customdata[2]}<br>"
            "BPRI Score: %{customdata[3]:.2f}<extra></extra>"
        ),
        name="Qualified Bowlers"
    ))
    
    fig.update_layout(
        title="<b>Clutch Suppression: Pressure Economy vs. Non-Pressure Baseline</b>",
        xaxis_title="Non-Pressure Economy (P < 45)",
        yaxis_title="Pressure Economy (P >= 45)",
        height=500
    )
    return apply_theme(fig)


def create_boundary_dot_scatter(df: pd.DataFrame, discipline: str = "batting") -> go.Figure:
    """Quadrant scatter plot of Boundary % vs Dot Ball %."""
    name_col = "striker_name" if discipline == "batting" else "bowler_name"
    pt_color = COLOR_BATTING if discipline == "batting" else COLOR_BOWLING
    
    fig = px.scatter(
        df,
        x="p_dot_pct",
        y="p_boundary_pct",
        text=name_col,
        size="p_balls_faced" if discipline == "batting" else "p_legal_balls",
        color="BPRI_Model1_Balanced",
        color_continuous_scale="Viridis",
        labels={
            "p_dot_pct": "Dot Ball Percentage (%)",
            "p_boundary_pct": "Boundary Percentage (%)",
            "BPRI_Model1_Balanced": "BPRI Score"
        },
        title=f"<b>{discipline.capitalize()} Execution Efficiency: Boundary % vs. Dot Ball % Under Pressure</b>"
    )
    fig.update_traces(textposition='top center', marker=dict(line=dict(color="#F8FAFC", width=1.2)))
    fig.update_layout(height=480)
    return apply_theme(fig)


def create_pressure_progression_chart(
    df_match: pd.DataFrame,
    match_title: str = "Match Pressure Progression"
) -> go.Figure:
    """Over-by-over ball-by-ball timeline of pressure score and key match events."""
    fig = go.Figure()
    
    # Smooth line of pressure score
    fig.add_trace(go.Scatter(
        x=df_match['innings_ball_num'],
        y=df_match['pressure_score'],
        mode='lines',
        line=dict(color=COLOR_BOWLING, width=2.5),
        name="Match Pressure (P)",
        hovertemplate="Ball: %{x}<br>Pressure Score: %{y:.1f}<extra></extra>"
    ))
    
    # High pressure threshold zone
    fig.add_hline(
        y=PRESSURE_THRESHOLD,
        line_dash="dash",
        line_color=COLOR_BATTING,
        annotation_text="High Pressure Threshold (P >= 45)",
        annotation_position="bottom right"
    )
    
    # Boundary markers
    boundaries = df_match[df_match['is_four'] | df_match['is_six']]
    if not boundaries.empty:
        fig.add_trace(go.Scatter(
            x=boundaries['innings_ball_num'],
            y=boundaries['pressure_score'],
            mode='markers',
            marker=dict(symbol='triangle-up', size=9, color=COLOR_EMERALD),
            name="Boundary Hit",
            hovertemplate="Boundary! Ball %{x}, Pressure: %{y:.1f}<extra></extra>"
        ))
        
    # Wicket markers
    wickets = df_match[df_match['is_wicket']]
    if not wickets.empty:
        fig.add_trace(go.Scatter(
            x=wickets['innings_ball_num'],
            y=wickets['pressure_score'],
            mode='markers',
            marker=dict(symbol='x', size=11, color=COLOR_CRITICAL, line=dict(width=2)),
            name="Wicket Fallen",
            hovertemplate="Wicket! Ball %{x}, Pressure: %{y:.1f}<extra></extra>"
        ))
        
    fig.update_layout(
        title=f"<b>{match_title}</b>",
        xaxis_title="Innings Legal Ball Number",
        yaxis_title="Pressure Score (P)",
        yaxis=dict(range=[0, 100]),
        height=450
    )
    return apply_theme(fig)
