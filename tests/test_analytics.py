"""
Unit tests for analytics and chart generation modules.
Verifies filtering, player profiling, and chart construction.
"""
import pytest
import pandas as pd
import plotly.graph_objects as go

from app.data_loader import (
    load_top10_batters,
    load_top10_bowlers,
    load_batting_rankings,
    load_bowling_rankings,
    load_deliveries_pressure
)
from app.analytics import (
    filter_batting_leaderboard,
    filter_bowling_leaderboard,
    get_batter_profile,
    get_bowler_profile,
    get_player_match_breakdown
)
from app.charts import (
    create_pressure_distribution_chart,
    create_bpri_ranking_chart,
    create_sr_comparison_scatter,
    create_econ_comparison_scatter,
    create_boundary_dot_scatter,
    create_pressure_progression_chart
)


def test_batting_filtering():
    """Verify that batting leaderboard filtering operates correctly."""
    df_bat = load_batting_rankings()
    
    # Filter by minimum balls
    f1 = filter_batting_leaderboard(df_bat, min_balls=100)
    assert (f1['p_balls_faced'] >= 100).all()
    assert len(f1) < len(df_bat)
    
    # Filter by BPRI range
    f2 = filter_batting_leaderboard(df_bat, bpri_range=(80.0, 90.0))
    assert (f2['BPRI_Model1_Balanced'] >= 80.0).all()
    assert (f2['BPRI_Model1_Balanced'] <= 90.0).all()
    
    # Filter by player
    f3 = filter_batting_leaderboard(df_bat, selected_players=['Rinku Singh', 'Tim David'])
    assert len(f3) == 2
    assert set(f3['striker_name']) == {'Rinku Singh', 'Tim David'}


def test_bowling_filtering():
    """Verify that bowling leaderboard filtering operates correctly."""
    df_bowl = load_bowling_rankings()
    
    # Filter by minimum legal balls
    f1 = filter_bowling_leaderboard(df_bowl, min_legal_balls=100)
    assert (f1['p_legal_balls'] >= 100).all()
    assert len(f1) < len(df_bowl)
    
    # Filter by economy range
    f2 = filter_bowling_leaderboard(df_bowl, econ_range=(3.0, 6.0))
    assert (f2['p_economy'] >= 3.0).all()
    assert (f2['p_economy'] <= 6.0).all()


def test_player_profiles():
    """Verify batter and bowler profile extraction."""
    # Batter Profile: Rinku Singh
    prof_bat = get_batter_profile("Rinku Singh")
    assert prof_bat is not None
    assert prof_bat['name'] == "Rinku Singh"
    assert prof_bat['rank'] == 1
    assert prof_bat['p_balls_faced'] == 253
    assert prof_bat['p_runs'] == 478
    assert abs(prof_bat['p_strike_rate'] - 188.93) < 0.1
    assert abs(prof_bat['unbiased_delta_sr'] - 45.13) < 0.1
    
    # Bowler Profile: Abrar Ahmed
    prof_bowl = get_bowler_profile("Abrar Ahmed")
    assert prof_bowl is not None
    assert prof_bowl['name'] == "Abrar Ahmed"
    assert prof_bowl['rank'] == 1
    assert prof_bowl['p_legal_balls'] == 141
    assert abs(prof_bowl['p_economy'] - 3.83) < 0.1
    assert prof_bowl['unbiased_delta_econ'] > 0  # positive suppression


def test_chart_generation():
    """Verify that all Plotly chart generation functions return valid figures."""
    df_top_bat = load_top10_batters()
    df_top_bowl = load_top10_bowlers()
    
    fig_bpri_bat = create_bpri_ranking_chart(df_top_bat, discipline="batting")
    assert isinstance(fig_bpri_bat, go.Figure)
    
    fig_bpri_bowl = create_bpri_ranking_chart(df_top_bowl, discipline="bowling")
    assert isinstance(fig_bpri_bowl, go.Figure)
    
    fig_sr = create_sr_comparison_scatter(df_top_bat)
    assert isinstance(fig_sr, go.Figure)
    
    fig_econ = create_econ_comparison_scatter(df_top_bowl)
    assert isinstance(fig_econ, go.Figure)
    
    fig_bdry = create_boundary_dot_scatter(df_top_bat, discipline="batting")
    assert isinstance(fig_bdry, go.Figure)
