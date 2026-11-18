"""
batting_features.py
Feature engineering module for batting under pressure.
Extracts volume, efficiency, boundary/dot profiles, tier breakdowns,
lift over baseline, and match-level consistency metrics.
"""

import numpy as np
import pandas as pd


def engineer_batting_features(df, bat_base, comp_base):
    """
    Constructs the comprehensive batting feature dataset under pressure.
    """
    df_bat = df[df['is_batter_ball']].copy()
    
    # 1. Overall player-level aggregation
    # Filter for pressure deliveries (P >= 45)
    p_df = df_bat[df_bat['is_pressure_delivery']].copy()
    
    # Outs under pressure
    outs_df = df[df['is_wicket'] & (df['dismissed_player_id'] == df['striker_id'])]
    p_outs = outs_df[outs_df['is_pressure_delivery']].groupby('striker_id').size()
    
    # Aggregations under pressure
    bat_p = p_df.groupby(['striker_id', 'striker_name']).agg(
        p_balls_faced=('runs', 'count'),
        p_runs=('runs', 'sum'),
        p_fours=('is_four', 'sum'),
        p_sixes=('is_six', 'sum'),
        p_dots=('runs', lambda x: (x == 0).sum()),
        p_matches=('match_id', 'nunique'),
        mean_pressure_faced=('pressure_score', 'mean')
    ).reset_index()
    
    bat_p['p_dismissals'] = bat_p['striker_id'].map(p_outs).fillna(0).astype(int)
    bat_p['p_strike_rate'] = (bat_p['p_runs'] / bat_p['p_balls_faced'] * 100.0).round(2)
    bat_p['p_boundary_pct'] = ((bat_p['p_fours'] + bat_p['p_sixes']) / bat_p['p_balls_faced'] * 100.0).round(2)
    bat_p['p_dot_pct'] = (bat_p['p_dots'] / bat_p['p_balls_faced'] * 100.0).round(2)
    bat_p['p_bat_avg'] = (bat_p['p_runs'] / bat_p['p_dismissals'].replace(0, np.nan)).round(2)
    bat_p['p_dismissal_rate'] = (bat_p['p_dismissals'] / bat_p['p_balls_faced'] * 100.0).round(2)
    
    # 2. Performance by Pressure Tiers (Low, Moderate, High, Critical)
    tiers = ['Low', 'Moderate', 'High', 'Critical']
    tier_stats = {}
    for t in tiers:
        t_sub = df_bat[df_bat['pressure_tier'] == t]
        t_agg = t_sub.groupby('striker_id').agg(
            balls=('runs', 'count'),
            runs=('runs', 'sum'),
            fours=('is_four', 'sum'),
            sixes=('is_six', 'sum')
        )
        t_agg[f'{t.lower()}_sr'] = (t_agg['runs'] / t_agg['balls'] * 100.0).round(2)
        t_agg = t_agg.rename(columns={
            'balls': f'{t.lower()}_balls',
            'runs': f'{t.lower()}_runs',
            'fours': f'{t.lower()}_fours',
            'sixes': f'{t.lower()}_sixes'
        })
        tier_stats[t] = t_agg
        
    for t in tiers:
        bat_p = bat_p.merge(tier_stats[t], on='striker_id', how='left')
        for col in [f'{t.lower()}_balls', f'{t.lower()}_runs', f'{t.lower()}_fours', f'{t.lower()}_sixes']:
            bat_p[col] = bat_p[col].fillna(0).astype(int)
        bat_p[f'{t.lower()}_sr'] = bat_p[f'{t.lower()}_sr'].fillna(0.0)
        
    # 3. Merge Career Baselines and compute relative lift
    bat_p = bat_p.merge(bat_base, on=['striker_id', 'striker_name'], how='left')
    
    # Relative Lift Metrics (Clutch Deltas)
    bat_p['delta_strike_rate'] = (bat_p['p_strike_rate'] - bat_p['career_bat_sr']).round(2)
    bat_p['delta_boundary_pct'] = (bat_p['p_boundary_pct'] - bat_p['career_boundary_pct']).round(2)
    bat_p['delta_dot_pct'] = (bat_p['p_dot_pct'] - bat_p['career_dot_pct']).round(2) # negative is better!
    
    # 4. Competition Weighted Normalization
    # Calculate player's pressure deliveries in IPL vs T20I vs Emerging
    p_comp = p_df.groupby(['striker_id', 'comp_category']).size().unstack(fill_value=0)
    for cat in ['IPL', 'T20I', 'T20_Emerging']:
        if cat not in p_comp.columns:
            p_comp[cat] = 0
            
    # Weighted expected league SR under pressure
    # Get pressure league SR per competition category
    p_comp_sr = df_bat[df_bat['is_pressure_delivery']].groupby('comp_category').agg(
        c_runs=('runs', 'sum'),
        c_balls=('runs', 'count')
    )
    p_comp_sr['league_p_sr'] = p_comp_sr['c_runs'] / p_comp_sr['c_balls'] * 100.0
    sr_map = p_comp_sr['league_p_sr'].to_dict()
    
    def calc_exp_sr(row):
        s_id = row['striker_id']
        if s_id in p_comp.index:
            counts = p_comp.loc[s_id]
            total = counts.sum()
            if total > 0:
                weighted_sr = sum(counts[cat] * sr_map.get(cat, 140.0) for cat in counts.index) / total
                return round(weighted_sr, 2)
        return 140.0
        
    bat_p['exp_league_p_sr'] = bat_p.apply(calc_exp_sr, axis=1)
    bat_p['comp_indexed_p_sr'] = (bat_p['p_strike_rate'] / bat_p['exp_league_p_sr'] * 100.0).round(2)
    
    # 5. Match-level Consistency Analysis
    match_bat = p_df.groupby(['striker_id', 'match_id']).agg(
        m_balls=('runs', 'count'),
        m_runs=('runs', 'sum')
    ).reset_index()
    match_bat['m_sr'] = match_bat['m_runs'] / match_bat['m_balls'] * 100.0
    
    # Consistency metrics across matches with >= 5 pressure balls
    m_sig = match_bat[match_bat['m_balls'] >= 5]
    m_consistency = m_sig.groupby('striker_id').agg(
        p_matches_sig=('match_id', 'count'),
        m_sr_std=('m_sr', 'std'),
        m_sr_median=('m_sr', 'median'),
        pct_matches_above_140=('m_sr', lambda x: (x >= 140.0).mean() * 100.0)
    ).reset_index()
    
    bat_p = bat_p.merge(m_consistency, on='striker_id', how='left')
    bat_p['p_matches_sig'] = bat_p['p_matches_sig'].fillna(0).astype(int)
    bat_p['m_sr_std'] = bat_p['m_sr_std'].fillna(0.0).round(2)
    bat_p['pct_matches_above_140'] = bat_p['pct_matches_above_140'].fillna(0.0).round(2)
    
    return bat_p
