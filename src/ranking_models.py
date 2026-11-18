"""
ranking_models.py
Statistical Analysis, Empirical Bayes Shrinkage, and Player Ranking Module.
Produces the Batting Pressure Reliability Index (BPRI) and Bowling Pressure Reliability Index (BPRI_bowl).
Generates model comparisons, sensitivity analyses, and the final Top 10 rankings.
"""

import os
import sys
import numpy as np
import pandas as pd

RAW_DIR = r"c:\Users\siddu\Downloads\rr hackathon\data\raw"
PROCESSED_DIR = r"c:\Users\siddu\Downloads\rr hackathon\data\processed"


def min_max_norm(series, invert=False):
    """
    Min-Max normalizes a series to [0, 100].
    If invert is True, lower raw values receive higher normalized scores.
    """
    s_min, s_max = series.min(), series.max()
    if s_max == s_min:
        return pd.Series(50.0, index=series.index)
    norm = (series - s_min) / (s_max - s_min) * 100.0
    return 100.0 - norm if invert else norm


def run_statistical_ranking():
    print("=" * 60)
    print("STARTING PHASE 3: STATISTICAL ANALYSIS & PLAYER RANKING")
    print("=" * 60)
    
    # 1. Load Processed Datasets
    print("\n[Step 1/6] Loading processed datasets...")
    df_deliv = pd.read_csv(os.path.join(PROCESSED_DIR, "deliveries_with_pressure.csv"), low_memory=False)
    bat_df = pd.read_csv(os.path.join(PROCESSED_DIR, "batting_pressure_features.csv"))
    bowl_df = pd.read_csv(os.path.join(PROCESSED_DIR, "bowling_pressure_features.csv"))
    
    # 2. Compute strictly Non-Pressure Baselines (P < 45) to eliminate self-referential bias
    print("\n[Step 2/6] Computing unbiased non-pressure baselines (P < 45)...")
    non_p = df_deliv[~df_deliv['is_pressure_delivery']].copy()
    
    # Non-pressure batting
    non_p_bat = non_p[non_p['is_batter_ball']].groupby(['striker_id', 'striker_name']).agg(
        np_balls=('runs', 'count'),
        np_runs=('runs', 'sum'),
        np_fours=('is_four', 'sum'),
        np_sixes=('is_six', 'sum'),
        np_dots=('runs', lambda x: (x == 0).sum())
    ).reset_index()
    non_p_bat['np_bat_sr'] = (non_p_bat['np_runs'] / non_p_bat['np_balls'] * 100.0).round(2)
    non_p_bat['np_boundary_pct'] = ((non_p_bat['np_fours'] + non_p_bat['np_sixes']) / non_p_bat['np_balls'] * 100.0).round(2)
    non_p_bat['np_dot_pct'] = (non_p_bat['np_dots'] / non_p_bat['np_balls'] * 100.0).round(2)
    
    bat_df = bat_df.merge(non_p_bat[['striker_id', 'np_balls', 'np_bat_sr', 'np_boundary_pct', 'np_dot_pct']], on='striker_id', how='left')
    bat_df['np_bat_sr'] = bat_df['np_bat_sr'].fillna(bat_df['career_bat_sr'])
    bat_df['unbiased_delta_sr'] = (bat_df['p_strike_rate'] - bat_df['np_bat_sr']).round(2)
    
    # Non-pressure bowling
    non_p_bowl = non_p[non_p['is_legal']].groupby(['bowler_id', 'bowler_name']).agg(
        np_legal_balls=('is_legal', 'sum'),
        np_runs_conceded=('bowler_runs_conceded', 'sum'),
        np_wickets=('is_bowler_wicket', 'sum')
    ).reset_index()
    
    dot_mask = (non_p['bowler_runs_conceded'] == 0) & non_p['is_legal']
    np_dots = non_p[dot_mask].groupby('bowler_id').size()
    bdry_mask = (non_p['is_four'] | non_p['is_six']) & non_p['is_legal']
    np_bdry = non_p[bdry_mask].groupby('bowler_id').size()
    
    non_p_bowl['np_dots'] = non_p_bowl['bowler_id'].map(np_dots).fillna(0).astype(int)
    non_p_bowl['np_boundaries'] = non_p_bowl['bowler_id'].map(np_bdry).fillna(0).astype(int)
    non_p_bowl['np_economy'] = (non_p_bowl['np_runs_conceded'] / (non_p_bowl['np_legal_balls'] / 6.0).replace(0, np.nan)).round(2)
    non_p_bowl['np_dot_pct'] = (non_p_bowl['np_dots'] / non_p_bowl['np_legal_balls'].replace(0, np.nan) * 100.0).round(2)
    non_p_bowl['np_boundary_pct'] = (non_p_bowl['np_boundaries'] / non_p_bowl['np_legal_balls'].replace(0, np.nan) * 100.0).round(2)
    
    bowl_df = bowl_df.merge(non_p_bowl[['bowler_id', 'np_legal_balls', 'np_economy', 'np_dot_pct', 'np_boundary_pct']], on='bowler_id', how='left')
    bowl_df['np_economy'] = bowl_df['np_economy'].fillna(bowl_df['career_economy'])
    bowl_df['unbiased_delta_econ'] = (bowl_df['np_economy'] - bowl_df['p_economy']).round(2)
    
    # 3. Batting Empirical Bayes & Multi-Criteria Ranking Models
    print("\n[Step 3/6] Applying Empirical Bayes shrinkage and ranking models for Batters...")
    b_qual = bat_df[bat_df['p_balls_faced'] >= 50].copy()
    
    # Prior for Batting Strike Rate
    mu_sr = b_qual['p_strike_rate'].mean()
    var_sr = b_qual['p_strike_rate'].var()
    var_within_bat = 28900.0 # sigma_within ~ 1.7 runs per ball
    n0_sr = var_within_bat / var_sr
    
    b_qual['w_sr'] = b_qual['p_balls_faced'] / (b_qual['p_balls_faced'] + n0_sr)
    b_qual['eb_p_sr'] = (b_qual['w_sr'] * b_qual['p_strike_rate'] + (1 - b_qual['w_sr']) * mu_sr).round(2)
    b_qual['se_p_sr'] = (np.sqrt(var_within_bat / b_qual['p_balls_faced'])).round(2)
    b_qual['ci95_sr_low'] = (b_qual['eb_p_sr'] - 1.96 * b_qual['se_p_sr']).round(2)
    b_qual['ci95_sr_high'] = (b_qual['eb_p_sr'] + 1.96 * b_qual['se_p_sr']).round(2)
    
    # Normalized Batting Features
    b_qual['norm_eb_sr'] = min_max_norm(b_qual['eb_p_sr'])
    b_qual['norm_delta_sr'] = min_max_norm(b_qual['unbiased_delta_sr'])
    b_qual['norm_boundary'] = min_max_norm(b_qual['p_boundary_pct'])
    b_qual['norm_dot'] = min_max_norm(b_qual['p_dot_pct'], invert=True)
    b_qual['norm_dismissal'] = min_max_norm(b_qual['p_dismissal_rate'], invert=True)
    b_qual['norm_consistency'] = min_max_norm(b_qual['pct_matches_above_140'])
    b_qual['norm_volume'] = np.clip(np.log(b_qual['p_balls_faced'] / 50.0) / np.log(300.0 / 50.0), 0.0, 1.0) * 100.0
    
    # Model 1: Balanced Multi-Criteria BPRI (Primary)
    b_qual['BPRI_Model1_Balanced'] = (
        0.25 * b_qual['norm_eb_sr'] +
        0.05 * b_qual['norm_boundary'] +
        0.05 * b_qual['norm_dot'] +
        0.25 * b_qual['norm_delta_sr'] +
        0.15 * b_qual['norm_consistency'] +
        0.10 * b_qual['norm_dismissal'] +
        0.15 * b_qual['norm_volume']
    ).round(2)
    
    # Model 2: Clutch-Lift Focus
    b_qual['BPRI_Model2_ClutchLift'] = (
        0.20 * b_qual['norm_eb_sr'] +
        0.05 * b_qual['norm_boundary'] +
        0.05 * b_qual['norm_dot'] +
        0.40 * b_qual['norm_delta_sr'] +
        0.15 * b_qual['norm_consistency'] +
        0.05 * b_qual['norm_dismissal'] +
        0.10 * b_qual['norm_volume']
    ).round(2)
    
    # Model 3: Absolute Execution Focus
    b_qual['BPRI_Model3_Absolute'] = (
        0.35 * b_qual['norm_eb_sr'] +
        0.10 * b_qual['norm_boundary'] +
        0.05 * b_qual['norm_dot'] +
        0.10 * b_qual['norm_delta_sr'] +
        0.15 * b_qual['norm_consistency'] +
        0.10 * b_qual['norm_dismissal'] +
        0.15 * b_qual['norm_volume']
    ).round(2)
    
    b_ranked = b_qual.sort_values(by='BPRI_Model1_Balanced', ascending=False).reset_index(drop=True)
    b_ranked['rank'] = b_ranked.index + 1
    
    # 4. Bowling Empirical Bayes & Multi-Criteria Ranking Models
    print("\n[Step 4/6] Applying Empirical Bayes shrinkage and ranking models for Bowlers...")
    bw_qual = bowl_df[bowl_df['p_legal_balls'] >= 60].copy()
    
    # Prior for Bowling Economy Rate
    mu_econ = bw_qual['p_economy'].mean()
    var_econ = bw_qual['p_economy'].var()
    var_within_bowl = 80.0
    b0_econ = var_within_bowl / var_econ
    
    bw_qual['w_econ'] = bw_qual['p_legal_balls'] / (bw_qual['p_legal_balls'] + b0_econ)
    bw_qual['eb_p_econ'] = (bw_qual['w_econ'] * bw_qual['p_economy'] + (1 - bw_qual['w_econ']) * mu_econ).round(2)
    bw_qual['se_p_econ'] = (np.sqrt(var_within_bowl / bw_qual['p_legal_balls'])).round(2)
    bw_qual['ci95_econ_low'] = (bw_qual['eb_p_econ'] - 1.96 * bw_qual['se_p_econ']).round(2)
    bw_qual['ci95_econ_high'] = (bw_qual['eb_p_econ'] + 1.96 * bw_qual['se_p_econ']).round(2)
    
    # Bowling Strike Rate (clean max 50)
    bw_qual['clean_bowl_sr'] = bw_qual['p_bowl_sr'].fillna(50.0).clip(upper=50.0)
    
    # Normalized Bowling Features
    bw_qual['norm_eb_econ'] = min_max_norm(bw_qual['eb_p_econ'], invert=True)
    bw_qual['norm_delta_econ'] = min_max_norm(bw_qual['unbiased_delta_econ'])
    bw_qual['norm_bowl_sr'] = min_max_norm(bw_qual['clean_bowl_sr'], invert=True)
    bw_qual['norm_dot'] = min_max_norm(bw_qual['p_dot_pct'])
    bw_qual['norm_boundary'] = min_max_norm(bw_qual['p_boundary_pct'], invert=True)
    bw_qual['norm_consistency'] = min_max_norm(bw_qual['pct_spells_sub_8_5'])
    bw_qual['norm_volume'] = np.clip(np.log(bw_qual['p_legal_balls'] / 60.0) / np.log(360.0 / 60.0), 0.0, 1.0) * 100.0
    
    # Model 1: Balanced Multi-Criteria Bowling BPRI (Primary)
    bw_qual['BPRI_Model1_Balanced'] = (
        0.25 * bw_qual['norm_eb_econ'] +
        0.05 * bw_qual['norm_dot'] +
        0.05 * bw_qual['norm_boundary'] +
        0.25 * bw_qual['norm_bowl_sr'] +
        0.20 * bw_qual['norm_delta_econ'] +
        0.10 * bw_qual['norm_consistency'] +
        0.10 * bw_qual['norm_volume']
    ).round(2)
    
    # Model 2: Wicket-Taking Specialist Focus
    bw_qual['BPRI_Model2_Wickets'] = (
        0.20 * bw_qual['norm_eb_econ'] +
        0.05 * bw_qual['norm_dot'] +
        0.05 * bw_qual['norm_boundary'] +
        0.35 * bw_qual['norm_bowl_sr'] +
        0.15 * bw_qual['norm_delta_econ'] +
        0.10 * bw_qual['norm_consistency'] +
        0.10 * bw_qual['norm_volume']
    ).round(2)
    
    # Model 3: Economy / Containment Specialist Focus
    bw_qual['BPRI_Model3_Economy'] = (
        0.35 * bw_qual['norm_eb_econ'] +
        0.10 * bw_qual['norm_dot'] +
        0.10 * bw_qual['norm_boundary'] +
        0.15 * bw_qual['norm_bowl_sr'] +
        0.15 * bw_qual['norm_delta_econ'] +
        0.10 * bw_qual['norm_consistency'] +
        0.05 * bw_qual['norm_volume']
    ).round(2)
    
    bw_ranked = bw_qual.sort_values(by='BPRI_Model1_Balanced', ascending=False).reset_index(drop=True)
    bw_ranked['rank'] = bw_ranked.index + 1
    
    # 5. Extract Top 10 and Sensitivity Comparisons
    print("\n[Step 5/6] Generating Top 10 lists and sensitivity comparisons...")
    top10_batters = b_ranked.head(10)[[
        'rank', 'striker_id', 'striker_name', 'BPRI_Model1_Balanced',
        'p_balls_faced', 'p_matches', 'p_runs', 'p_strike_rate', 'eb_p_sr',
        'p_boundary_pct', 'p_dot_pct', 'p_dismissal_rate',
        'np_bat_sr', 'unbiased_delta_sr', 'pct_matches_above_140',
        'se_p_sr', 'ci95_sr_low', 'ci95_sr_high'
    ]]
    
    top10_bowlers = bw_ranked.head(10)[[
        'rank', 'bowler_id', 'bowler_name', 'BPRI_Model1_Balanced',
        'p_legal_balls', 'p_overs', 'p_matches', 'p_wickets',
        'p_economy', 'eb_p_econ', 'p_bowl_sr',
        'p_dot_pct', 'p_boundary_pct',
        'np_economy', 'unbiased_delta_econ', 'pct_spells_sub_8_5',
        'se_p_econ', 'ci95_econ_low', 'ci95_econ_high'
    ]]
    
    # Model comparisons
    bat_comp = b_ranked.head(20)[[
        'rank', 'striker_name', 'p_balls_faced', 'p_strike_rate', 'unbiased_delta_sr',
        'BPRI_Model1_Balanced', 'BPRI_Model2_ClutchLift', 'BPRI_Model3_Absolute'
    ]]
    
    bowl_comp = bw_ranked.head(20)[[
        'rank', 'bowler_name', 'p_legal_balls', 'p_economy', 'p_bowl_sr', 'unbiased_delta_econ',
        'BPRI_Model1_Balanced', 'BPRI_Model2_Wickets', 'BPRI_Model3_Economy'
    ]]
    
    # Threshold sensitivity: check Top 10 overlap across thresholds (40, 50, 60, 75 balls)
    sens_records = []
    for b_cut in [40, 50, 60, 75]:
        b_sub = bat_df[bat_df['p_balls_faced'] >= b_cut].copy()
        b_sub['w_sr'] = b_sub['p_balls_faced'] / (b_sub['p_balls_faced'] + n0_sr)
        b_sub['eb_p_sr'] = b_sub['w_sr'] * b_sub['p_strike_rate'] + (1 - b_sub['w_sr']) * mu_sr
        b_sub['norm_eb_sr'] = min_max_norm(b_sub['eb_p_sr'])
        b_sub['norm_delta_sr'] = min_max_norm(b_sub['unbiased_delta_sr'])
        b_sub['norm_boundary'] = min_max_norm(b_sub['p_boundary_pct'])
        b_sub['norm_dot'] = min_max_norm(b_sub['p_dot_pct'], invert=True)
        b_sub['norm_dismissal'] = min_max_norm(b_sub['p_dismissal_rate'], invert=True)
        b_sub['norm_consistency'] = min_max_norm(b_sub['pct_matches_above_140'])
        b_sub['norm_volume'] = np.clip(np.log(b_sub['p_balls_faced'] / b_cut) / np.log(300.0 / b_cut), 0.0, 1.0) * 100.0
        b_sub['score'] = (
            0.25 * b_sub['norm_eb_sr'] + 0.05 * b_sub['norm_boundary'] + 0.05 * b_sub['norm_dot'] +
            0.25 * b_sub['norm_delta_sr'] + 0.15 * b_sub['norm_consistency'] + 0.10 * b_sub['norm_dismissal'] + 0.15 * b_sub['norm_volume']
        )
        top10_names = b_sub.sort_values(by='score', ascending=False).head(10)['striker_name'].tolist()
        sens_records.append({
            'Category': 'Batting',
            'Threshold': f'>= {b_cut} balls',
            'Eligible_Count': len(b_sub),
            'Top10': ", ".join(top10_names)
        })
        
    for bw_cut in [48, 60, 72, 90]:
        bw_sub = bowl_df[bowl_df['p_legal_balls'] >= bw_cut].copy()
        bw_sub['w_econ'] = bw_sub['p_legal_balls'] / (bw_sub['p_legal_balls'] + b0_econ)
        bw_sub['eb_p_econ'] = bw_sub['w_econ'] * bw_sub['p_economy'] + (1 - bw_sub['w_econ']) * mu_econ
        bw_sub['clean_bowl_sr'] = bw_sub['p_bowl_sr'].fillna(50.0).clip(upper=50.0)
        bw_sub['norm_eb_econ'] = min_max_norm(bw_sub['eb_p_econ'], invert=True)
        bw_sub['norm_delta_econ'] = min_max_norm(bw_sub['unbiased_delta_econ'])
        bw_sub['norm_bowl_sr'] = min_max_norm(bw_sub['clean_bowl_sr'], invert=True)
        bw_sub['norm_dot'] = min_max_norm(bw_sub['p_dot_pct'])
        bw_sub['norm_boundary'] = min_max_norm(bw_sub['p_boundary_pct'], invert=True)
        bw_sub['norm_consistency'] = min_max_norm(bw_sub['pct_spells_sub_8_5'])
        bw_sub['norm_volume'] = np.clip(np.log(bw_sub['p_legal_balls'] / bw_cut) / np.log(360.0 / bw_cut), 0.0, 1.0) * 100.0
        bw_sub['score'] = (
            0.25 * bw_sub['norm_eb_econ'] + 0.05 * bw_sub['norm_dot'] + 0.05 * bw_sub['norm_boundary'] +
            0.25 * bw_sub['norm_bowl_sr'] + 0.20 * bw_sub['norm_delta_econ'] + 0.10 * bw_sub['norm_consistency'] + 0.10 * bw_sub['norm_volume']
        )
        top10_names = bw_sub.sort_values(by='score', ascending=False).head(10)['bowler_name'].tolist()
        sens_records.append({
            'Category': 'Bowling',
            'Threshold': f'>= {bw_cut} legal balls',
            'Eligible_Count': len(bw_sub),
            'Top10': ", ".join(top10_names)
        })
        
    df_sens = pd.DataFrame(sens_records)
    
    # 6. Save All Required Outputs
    print("\n[Step 6/6] Saving Phase 3 outputs...")
    b_ranked.to_csv(os.path.join(PROCESSED_DIR, "batting_ranking_full.csv"), index=False)
    bw_ranked.to_csv(os.path.join(PROCESSED_DIR, "bowling_ranking_full.csv"), index=False)
    top10_batters.to_csv(os.path.join(PROCESSED_DIR, "top10_batters.csv"), index=False)
    top10_bowlers.to_csv(os.path.join(PROCESSED_DIR, "top10_bowlers.csv"), index=False)
    bat_comp.to_csv(os.path.join(PROCESSED_DIR, "batting_model_comparison.csv"), index=False)
    bowl_comp.to_csv(os.path.join(PROCESSED_DIR, "bowling_model_comparison.csv"), index=False)
    df_sens.to_csv(os.path.join(PROCESSED_DIR, "ranking_sensitivity.csv"), index=False)
    
    print("  Saved: batting_ranking_full.csv")
    print("  Saved: bowling_ranking_full.csv")
    print("  Saved: top10_batters.csv")
    print("  Saved: top10_bowlers.csv")
    print("  Saved: batting_model_comparison.csv")
    print("  Saved: bowling_model_comparison.csv")
    print("  Saved: ranking_sensitivity.csv")
    
    print("\n" + "=" * 60)
    print("TOP 10 BATTERS UNDER PRESSURE (BPRI)")
    print("=" * 60)
    print(top10_batters[['rank', 'striker_name', 'BPRI_Model1_Balanced', 'p_balls_faced', 'p_strike_rate', 'eb_p_sr', 'unbiased_delta_sr', 'pct_matches_above_140']])
    
    print("\n" + "=" * 60)
    print("TOP 10 BOWLERS UNDER PRESSURE (BPRI_bowl)")
    print("=" * 60)
    print(top10_bowlers[['rank', 'bowler_name', 'BPRI_Model1_Balanced', 'p_legal_balls', 'p_wickets', 'p_economy', 'eb_p_econ', 'unbiased_delta_econ', 'p_bowl_sr']])
    
    return b_ranked, bw_ranked, top10_batters, top10_bowlers, df_sens


if __name__ == "__main__":
    run_statistical_ranking()
