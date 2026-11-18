"""
baselines.py
Baseline performance calculation module.
Computes competition-level, season-level, and player-level career baselines
to enable fair context normalization and lift calculations.
"""

import numpy as np
import pandas as pd


def compute_competition_baselines(df):
    """
    Computes macro baseline statistics for each competition category and season.
    """
    df_legal = df[df['is_legal']].copy()
    df_bat = df[df['is_batter_ball']].copy()
    
    # Competition category baseline
    comp_base = df.groupby('comp_category').agg(
        total_deliveries=('runs', 'count'),
        batter_balls=('is_batter_ball', 'sum'),
        batter_runs=('runs', 'sum'),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum'),
        legal_balls=('is_legal', 'sum'),
        bowler_runs=('bowler_runs_conceded', 'sum'),
        bowler_wickets=('is_bowler_wicket', 'sum')
    )
    
    dot_mask = (df['bowler_runs_conceded'] == 0) & df['is_legal']
    dots = df[dot_mask].groupby('comp_category').size()
    comp_base['dots'] = dots
    
    comp_base['league_bat_sr'] = (comp_base['batter_runs'] / comp_base['batter_balls'] * 100.0).round(2)
    comp_base['league_boundary_pct'] = ((comp_base['fours'] + comp_base['sixes']) / comp_base['batter_balls'] * 100.0).round(2)
    comp_base['league_economy'] = (comp_base['bowler_runs'] / (comp_base['legal_balls'] / 6.0)).round(2)
    comp_base['league_bowl_sr'] = (comp_base['legal_balls'] / comp_base['bowler_wickets']).round(2)
    comp_base['league_dot_pct'] = (comp_base['dots'] / comp_base['legal_balls'] * 100.0).round(2)
    
    return comp_base


def compute_player_career_baselines(df):
    """
    Computes overall career baselines for each batter and bowler across the full dataset.
    """
    # 1. Batting Career Baselines
    bat_df = df[df['is_batter_ball']].copy()
    
    bat_base = bat_df.groupby(['striker_id', 'striker_name']).agg(
        career_balls_faced=('runs', 'count'),
        career_runs=('runs', 'sum'),
        career_fours=('is_four', 'sum'),
        career_sixes=('is_six', 'sum'),
        career_dots=('runs', lambda x: (x == 0).sum())
    ).reset_index()
    
    # Exact dismissals of striker
    outs_df = df[df['is_wicket'] & (df['dismissed_player_id'] == df['striker_id'])]
    outs_count = outs_df.groupby('striker_id').size()
    bat_base['career_dismissals'] = bat_base['striker_id'].map(outs_count).fillna(0).astype(int)
    
    bat_base['career_bat_sr'] = (bat_base['career_runs'] / bat_base['career_balls_faced'] * 100.0).round(2)
    bat_base['career_boundary_pct'] = (
        (bat_base['career_fours'] + bat_base['career_sixes']) / bat_base['career_balls_faced'] * 100.0
    ).round(2)
    bat_base['career_dot_pct'] = (bat_base['career_dots'] / bat_base['career_balls_faced'] * 100.0).round(2)
    bat_base['career_bat_avg'] = (
        bat_base['career_runs'] / bat_base['career_dismissals'].replace(0, np.nan)
    ).round(2)
    
    # 2. Bowling Career Baselines
    bowl_df = df[df['is_legal']].copy()
    
    bowl_base = df.groupby(['bowler_id', 'bowler_name']).agg(
        career_legal_balls=('is_legal', 'sum'),
        career_runs_conceded=('bowler_runs_conceded', 'sum'),
        career_wickets=('is_bowler_wicket', 'sum')
    ).reset_index()
    
    dot_mask = (df['bowler_runs_conceded'] == 0) & df['is_legal']
    bowl_dots = df[dot_mask].groupby('bowler_id').size()
    bowl_base['career_dots'] = bowl_base['bowler_id'].map(bowl_dots).fillna(0).astype(int)
    
    fours_sixes_mask = df['is_four'] | df['is_six']
    bowl_bdry = df[fours_sixes_mask & df['is_legal']].groupby('bowler_id').size()
    bowl_base['career_boundaries_conceded'] = bowl_base['bowler_id'].map(bowl_bdry).fillna(0).astype(int)
    
    bowl_base['career_economy'] = (
        bowl_base['career_runs_conceded'] / (bowl_base['career_legal_balls'] / 6.0).replace(0, np.nan)
    ).round(2)
    bowl_base['career_bowl_sr'] = (
        bowl_base['career_legal_balls'] / bowl_base['career_wickets'].replace(0, np.nan)
    ).round(2)
    bowl_base['career_bowl_avg'] = (
        bowl_base['career_runs_conceded'] / bowl_base['career_wickets'].replace(0, np.nan)
    ).round(2)
    bowl_base['career_dot_pct'] = (
        bowl_base['career_dots'] / bowl_base['career_legal_balls'].replace(0, np.nan) * 100.0
    ).round(2)
    bowl_base['career_boundary_pct'] = (
        bowl_base['career_boundaries_conceded'] / bowl_base['career_legal_balls'].replace(0, np.nan) * 100.0
    ).round(2)
    
    return bat_base, bowl_base
