"""
bowling_features.py
Feature engineering module for bowling under pressure.
Extracts volume, efficiency, wicket-taking strike rates, boundary/dot profiles,
tier breakdowns, lift over baseline, and match-level consistency metrics.
"""

import numpy as np
import pandas as pd


def engineer_bowling_features(df, bowl_base, comp_base):
    """
    Constructs the comprehensive bowling feature dataset under pressure.
    """
    # Pressure deliveries
    p_df = df[df['is_pressure_delivery']].copy()
    
    # 1. Overall player-level aggregation
    # Note: bowler metrics rely strictly on legal deliveries and correct bowler runs conceded
    dot_mask = (p_df['bowler_runs_conceded'] == 0) & p_df['is_legal']
    bdry_mask = (p_df['is_four'] | p_df['is_six']) & p_df['is_legal']
    
    bowl_p = p_df.groupby(['bowler_id', 'bowler_name']).agg(
        p_legal_balls=('is_legal', 'sum'),
        p_runs_conceded=('bowler_runs_conceded', 'sum'),
        p_wickets=('is_bowler_wicket', 'sum'),
        p_matches=('match_id', 'nunique'),
        mean_pressure_bowled=('pressure_score', 'mean')
    ).reset_index()
    
    dots_count = p_df[dot_mask].groupby('bowler_id').size()
    bdry_count = p_df[bdry_mask].groupby('bowler_id').size()
    
    bowl_p['p_dots'] = bowl_p['bowler_id'].map(dots_count).fillna(0).astype(int)
    bowl_p['p_boundaries_conceded'] = bowl_p['bowler_id'].map(bdry_count).fillna(0).astype(int)
    
    bowl_p['p_overs'] = (bowl_p['p_legal_balls'] // 6) + (bowl_p['p_legal_balls'] % 6) / 10.0
    bowl_p['p_economy'] = (
        bowl_p['p_runs_conceded'] / (bowl_p['p_legal_balls'] / 6.0).replace(0, np.nan)
    ).round(2)
    bowl_p['p_bowl_sr'] = (
        bowl_p['p_legal_balls'] / bowl_p['p_wickets'].replace(0, np.nan)
    ).round(2)
    bowl_p['p_bowl_avg'] = (
        bowl_p['p_runs_conceded'] / bowl_p['p_wickets'].replace(0, np.nan)
    ).round(2)
    bowl_p['p_dot_pct'] = (
        bowl_p['p_dots'] / bowl_p['p_legal_balls'].replace(0, np.nan) * 100.0
    ).round(2)
    bowl_p['p_boundary_pct'] = (
        bowl_p['p_boundaries_conceded'] / bowl_p['p_legal_balls'].replace(0, np.nan) * 100.0
    ).round(2)
    
    # 2. Performance by Pressure Tiers (Low, Moderate, High, Critical)
    tiers = ['Low', 'Moderate', 'High', 'Critical']
    tier_stats = {}
    for t in tiers:
        t_sub = df[df['pressure_tier'] == t]
        t_agg = t_sub.groupby('bowler_id').agg(
            legal_balls=('is_legal', 'sum'),
            runs=('bowler_runs_conceded', 'sum'),
            wickets=('is_bowler_wicket', 'sum')
        )
        t_agg[f'{t.lower()}_econ'] = (
            t_agg['runs'] / (t_agg['legal_balls'] / 6.0).replace(0, np.nan)
        ).round(2)
        t_agg = t_agg.rename(columns={
            'legal_balls': f'{t.lower()}_balls',
            'runs': f'{t.lower()}_runs',
            'wickets': f'{t.lower()}_wickets'
        })
        tier_stats[t] = t_agg
        
    for t in tiers:
        bowl_p = bowl_p.merge(tier_stats[t], on='bowler_id', how='left')
        for col in [f'{t.lower()}_balls', f'{t.lower()}_runs', f'{t.lower()}_wickets']:
            bowl_p[col] = bowl_p[col].fillna(0).astype(int)
        bowl_p[f'{t.lower()}_econ'] = bowl_p[f'{t.lower()}_econ'].fillna(0.0)
        
    # 3. Merge Career Baselines and compute relative lift
    bowl_p = bowl_p.merge(bowl_base, on=['bowler_id', 'bowler_name'], how='left')
    
    # Relative Lift Metrics
    # Positive delta_economy means bowler improved (conceded fewer runs under pressure than baseline)
    bowl_p['delta_economy'] = (bowl_p['career_economy'] - bowl_p['p_economy']).round(2)
    bowl_p['delta_dot_pct'] = (bowl_p['p_dot_pct'] - bowl_p['career_dot_pct']).round(2)
    bowl_p['delta_boundary_pct'] = (bowl_p['career_boundary_pct'] - bowl_p['p_boundary_pct']).round(2)
    bowl_p['delta_bowl_sr'] = (bowl_p['career_bowl_sr'] - bowl_p['p_bowl_sr']).round(2)
    
    # 4. Competition Weighted Normalization
    p_comp = p_df[p_df['is_legal']].groupby(['bowler_id', 'comp_category']).size().unstack(fill_value=0)
    for cat in ['IPL', 'T20I', 'T20_Emerging']:
        if cat not in p_comp.columns:
            p_comp[cat] = 0
            
    # League pressure economy per competition category
    p_comp_econ = p_df[p_df['is_legal']].groupby('comp_category').agg(
        c_runs=('bowler_runs_conceded', 'sum'),
        c_balls=('is_legal', 'sum')
    )
    p_comp_econ['league_p_econ'] = p_comp_econ['c_runs'] / (p_comp_econ['c_balls'] / 6.0)
    econ_map = p_comp_econ['league_p_econ'].to_dict()
    
    def calc_exp_econ(row):
        b_id = row['bowler_id']
        if b_id in p_comp.index:
            counts = p_comp.loc[b_id]
            total = counts.sum()
            if total > 0:
                weighted_econ = sum(counts[cat] * econ_map.get(cat, 9.5) for cat in counts.index) / total
                return round(weighted_econ, 2)
        return 9.5
        
    bowl_p['exp_league_p_econ'] = bowl_p.apply(calc_exp_econ, axis=1)
    # Higher index means better than league average
    bowl_p['comp_indexed_p_econ'] = (
        bowl_p['exp_league_p_econ'] / bowl_p['p_economy'].replace(0, np.nan) * 100.0
    ).round(2)
    
    # 5. Match-level Consistency Analysis
    match_bowl = p_df[p_df['is_legal']].groupby(['bowler_id', 'match_id']).agg(
        m_balls=('is_legal', 'sum'),
        m_runs=('bowler_runs_conceded', 'sum'),
        m_wickets=('is_bowler_wicket', 'sum')
    ).reset_index()
    match_bowl['m_econ'] = match_bowl['m_runs'] / (match_bowl['m_balls'] / 6.0)
    
    # Consistency across matches with >= 6 pressure legal deliveries (at least 1 full pressure over)
    m_sig = match_bowl[match_bowl['m_balls'] >= 6]
    m_consistency = m_sig.groupby('bowler_id').agg(
        p_spells_sig=('match_id', 'count'),
        m_econ_std=('m_econ', 'std'),
        m_econ_median=('m_econ', 'median'),
        pct_spells_sub_8_5=('m_econ', lambda x: (x <= 8.5).mean() * 100.0)
    ).reset_index()
    
    bowl_p = bowl_p.merge(m_consistency, on='bowler_id', how='left')
    bowl_p['p_spells_sig'] = bowl_p['p_spells_sig'].fillna(0).astype(int)
    bowl_p['m_econ_std'] = bowl_p['m_econ_std'].fillna(0.0).round(2)
    bowl_p['pct_spells_sub_8_5'] = bowl_p['pct_spells_sub_8_5'].fillna(0.0).round(2)
    
    return bowl_p
