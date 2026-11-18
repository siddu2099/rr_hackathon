"""
Analytics helper module for SupeRR Selector Season 2 Dashboard.
Computes player profiles, filtered views, and match-level breakdowns.
"""
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np

from app.data_loader import (
    load_batting_rankings,
    load_bowling_rankings,
    load_top10_batters,
    load_top10_bowlers
)


def filter_batting_leaderboard(
    df: pd.DataFrame,
    min_balls: int = 50,
    bpri_range: tuple = (70.0, 100.0),
    sr_range: tuple = (100.0, 250.0),
    selected_players: Optional[List[str]] = None
) -> pd.DataFrame:
    """Filter qualified batting rankings based on interactive sidebar controls."""
    filtered = df.copy()
    
    if 'p_balls_faced' in filtered.columns:
        filtered = filtered[filtered['p_balls_faced'] >= min_balls]
        
    if 'BPRI_Model1_Balanced' in filtered.columns:
        filtered = filtered[
            (filtered['BPRI_Model1_Balanced'] >= bpri_range[0]) &
            (filtered['BPRI_Model1_Balanced'] <= bpri_range[1])
        ]
        
    if 'p_strike_rate' in filtered.columns:
        filtered = filtered[
            (filtered['p_strike_rate'] >= sr_range[0]) &
            (filtered['p_strike_rate'] <= sr_range[1])
        ]
        
    if selected_players and len(selected_players) > 0:
        filtered = filtered[filtered['striker_name'].isin(selected_players)]
        
    return filtered.sort_values(by='BPRI_Model1_Balanced', ascending=False)


def filter_bowling_leaderboard(
    df: pd.DataFrame,
    min_legal_balls: int = 60,
    bpri_range: tuple = (70.0, 100.0),
    econ_range: tuple = (3.0, 12.0),
    min_wickets: int = 0,
    selected_players: Optional[List[str]] = None
) -> pd.DataFrame:
    """Filter qualified bowling rankings based on interactive sidebar controls."""
    filtered = df.copy()
    
    if 'p_legal_balls' in filtered.columns:
        filtered = filtered[filtered['p_legal_balls'] >= min_legal_balls]
        
    if 'BPRI_Model1_Balanced' in filtered.columns:
        filtered = filtered[
            (filtered['BPRI_Model1_Balanced'] >= bpri_range[0]) &
            (filtered['BPRI_Model1_Balanced'] <= bpri_range[1])
        ]
        
    if 'p_economy' in filtered.columns:
        filtered = filtered[
            (filtered['p_economy'] >= econ_range[0]) &
            (filtered['p_economy'] <= econ_range[1])
        ]
        
    if 'p_wickets' in filtered.columns:
        filtered = filtered[filtered['p_wickets'] >= min_wickets]
        
    if selected_players and len(selected_players) > 0:
        filtered = filtered[filtered['bowler_name'].isin(selected_players)]
        
    return filtered.sort_values(by='BPRI_Model1_Balanced', ascending=False)


def get_batter_profile(player_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve detailed statistics and BPRI breakdown for a selected batter."""
    df_rank = load_batting_rankings()
    row = df_rank[df_rank['striker_name'] == player_name]
    
    if row.empty:
        # Fallback to Top 10
        df_top = load_top10_batters()
        row = df_top[df_top['striker_name'] == player_name]
        if row.empty:
            return None
            
    r = row.iloc[0]
    
    profile = {
        'name': r.get('striker_name', player_name),
        'player_id': r.get('striker_id', 'N/A'),
        'rank': int(r.get('rank', 0)),
        'bpri': float(r.get('BPRI_Model1_Balanced', 0.0)),
        'p_balls_faced': int(r.get('p_balls_faced', 0)),
        'p_runs': int(r.get('p_runs', 0)),
        'p_strike_rate': float(r.get('p_strike_rate', 0.0)),
        'eb_p_sr': float(r.get('eb_p_sr', r.get('p_strike_rate', 0.0))),
        'p_boundary_pct': float(r.get('p_boundary_pct', 0.0)),
        'p_dot_pct': float(r.get('p_dot_pct', 0.0)),
        'p_dismissal_rate': float(r.get('p_dismissal_rate', 0.0)),
        'p_matches': int(r.get('p_matches', 0)),
        'np_bat_sr': float(r.get('np_bat_sr', 0.0)) if pd.notna(r.get('np_bat_sr')) else None,
        'unbiased_delta_sr': float(r.get('unbiased_delta_sr', 0.0)) if pd.notna(r.get('unbiased_delta_sr')) else None,
        'consistency_pct': float(r.get('pct_matches_above_140', 0.0)),
        # Tier-wise stats if present in full ranking
        'low_sr': r.get('low_sr', None),
        'moderate_sr': r.get('moderate_sr', None),
        'high_sr': r.get('high_sr', None),
        'critical_sr': r.get('critical_sr', None)
    }
    return profile


def get_bowler_profile(player_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve detailed statistics and BPRI breakdown for a selected bowler."""
    df_rank = load_bowling_rankings()
    row = df_rank[df_rank['bowler_name'] == player_name]
    
    if row.empty:
        df_top = load_top10_bowlers()
        row = df_top[df_top['bowler_name'] == player_name]
        if row.empty:
            return None
            
    r = row.iloc[0]
    
    profile = {
        'name': r.get('bowler_name', player_name),
        'player_id': r.get('bowler_id', 'N/A'),
        'rank': int(r.get('rank', 0)),
        'bpri': float(r.get('BPRI_Model1_Balanced', 0.0)),
        'p_legal_balls': int(r.get('p_legal_balls', 0)),
        'p_overs': float(r.get('p_overs', 0.0)),
        'p_runs_conceded': int(r.get('p_runs_conceded', 0)),
        'p_wickets': int(r.get('p_wickets', 0)),
        'p_economy': float(r.get('p_economy', 0.0)),
        'eb_p_econ': float(r.get('eb_p_econ', r.get('p_economy', 0.0))),
        'p_bowl_sr': float(r.get('p_bowl_sr', 0.0)),
        'p_dot_pct': float(r.get('p_dot_pct', 0.0)),
        'p_boundary_pct': float(r.get('p_boundary_pct', 0.0)),
        'p_matches': int(r.get('p_matches', 0)),
        'np_economy': float(r.get('np_economy', 0.0)) if pd.notna(r.get('np_economy')) else None,
        'unbiased_delta_econ': float(r.get('unbiased_delta_econ', 0.0)) if pd.notna(r.get('unbiased_delta_econ')) else None,
        'consistency_pct': float(r.get('pct_spells_sub_8_5', 0.0)),
        # Tier-wise stats if present in full ranking
        'low_econ': r.get('low_econ', None),
        'moderate_econ': r.get('moderate_econ', None),
        'high_econ': r.get('high_econ', None),
        'critical_econ': r.get('critical_econ', None)
    }
    return profile


def get_player_match_breakdown(
    player_id: int,
    role: str = 'batter',
    df_deliv: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """Extract match-level pressure logs for a given player."""
    if df_deliv is None or df_deliv.empty:
        return pd.DataFrame()
        
    p_deliv = df_deliv[df_deliv['is_pressure_delivery']]
    
    if role == 'batter':
        sub = p_deliv[(p_deliv['striker_id'] == player_id) & (p_deliv['is_batter_ball'])]
        if sub.empty:
            return pd.DataFrame()
        agg = sub.groupby(['match_id', 'innings', 'season', 'comp_category'], observed=True).agg(
            pressure_balls=('runs', 'count'),
            pressure_runs=('runs', 'sum'),
            fours=('is_four', 'sum'),
            sixes=('is_six', 'sum'),
            mean_pressure=('pressure_score', 'mean')
        ).reset_index()
        agg['strike_rate'] = (agg['pressure_runs'] / agg['pressure_balls']) * 100.0
        return agg.sort_values(by='pressure_runs', ascending=False)
        
    else:  # bowler
        sub = p_deliv[p_deliv['bowler_id'] == player_id]
        if sub.empty:
            return pd.DataFrame()
        agg = sub.groupby(['match_id', 'innings', 'season', 'comp_category'], observed=True).agg(
            legal_balls=('is_legal', 'sum'),
            runs_conceded=('bowler_runs_conceded', 'sum'),
            wickets=('is_bowler_wicket', 'sum'),
            dots=('runs', lambda x: (x == 0).sum()),
            mean_pressure=('pressure_score', 'mean')
        ).reset_index()
        agg = agg[agg['legal_balls'] > 0]
        agg['economy'] = (agg['runs_conceded'] / (agg['legal_balls'] / 6.0))
        return agg.sort_values(by='wickets', ascending=False)
