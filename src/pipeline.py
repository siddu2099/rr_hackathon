"""
pipeline.py
End-to-end execution pipeline for Phase 2: Pressure Framework & Feature Engineering.
Loads raw data, performs pre-delivery reconstruction, calculates pressure,
engineers batting and bowling features, applies competition baselines,
runs validation checks, and saves processed datasets under data/processed/.
"""

import os
import sys
import numpy as np
import pandas as pd

# Add src to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from match_state import clean_delivery_metadata, reconstruct_pre_delivery_state
from pressure_model import apply_pressure_model
from baselines import compute_competition_baselines, compute_player_career_baselines
from batting_features import engineer_batting_features
from bowling_features import engineer_bowling_features


RAW_DIR = r"c:\Users\siddu\Downloads\rr hackathon\data\raw"
PROCESSED_DIR = r"c:\Users\siddu\Downloads\rr hackathon\data\processed"


def run_pipeline():
    print("=" * 60)
    print("STARTING PHASE 2 DATA PROCESSING & FEATURE ENGINEERING")
    print("=" * 60)
    
    # 1. Load Raw Datasets
    print("\n[Step 1/7] Loading raw datasets from data/raw/...")
    df_bbb = pd.read_csv(os.path.join(RAW_DIR, "ball_by_ball.csv"))
    df_matches = pd.read_csv(os.path.join(RAW_DIR, "matches.csv"))
    df_comp = pd.read_csv(os.path.join(RAW_DIR, "competitions.csv"))
    df_map = pd.read_csv(os.path.join(RAW_DIR, "competition_team_player_mapping.csv"))
    
    print(f"  Loaded ball_by_ball: {len(df_bbb):,} rows")
    print(f"  Loaded matches: {len(df_matches):,} rows")
    print(f"  Loaded competitions: {len(df_comp):,} rows")
    
    # Enrich matches with competition info
    m_comp = df_matches.merge(df_comp[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')
    comp_map = m_comp.set_index('match_id')[['comp_name', 'match_format', 'season']].to_dict('index')
    
    def get_comp_category(c_name):
        c_lower = str(c_name).lower()
        if 'ipl' in c_lower or 'indian premier league' in c_lower:
            return 'IPL'
        elif 'emerging' in c_lower or 'rising stars' in c_lower:
            return 'T20_Emerging'
        else:
            return 'T20I'
            
    df_bbb['comp_name'] = df_bbb['match_id'].map(lambda x: comp_map.get(x, {}).get('comp_name', 'Unknown'))
    df_bbb['match_format'] = df_bbb['match_id'].map(lambda x: comp_map.get(x, {}).get('match_format', 'Unknown'))
    df_bbb['season'] = df_bbb['match_id'].map(lambda x: comp_map.get(x, {}).get('season', 'Unknown'))
    df_bbb['comp_category'] = df_bbb['comp_name'].apply(get_comp_category)
    
    # 2. Clean Delivery Metadata & Bowling Accounting
    print("\n[Step 2/7] Cleaning delivery metadata and standardizing rules...")
    df_clean = clean_delivery_metadata(df_bbb)
    
    # 3. Pre-Delivery State Reconstruction
    print("\n[Step 3/7] Reconstructing chronological pre-delivery state (zero leakage)...")
    df_state = reconstruct_pre_delivery_state(df_clean, df_matches)
    
    # 4. Continuous Pressure & Tier Classification
    print("\n[Step 4/7] Applying continuous pressure models & tier classification...")
    df_pressure = apply_pressure_model(df_state)
    
    print("\n  --- Pressure Tier Distribution Across Deliveries ---")
    tier_counts = df_pressure['pressure_tier'].value_counts()
    tier_pcts = (df_pressure['pressure_tier'].value_counts(normalize=True) * 100).round(2)
    tier_summary = pd.DataFrame({'Deliveries': tier_counts, 'Percentage': tier_pcts})
    print(tier_summary)
    
    # 5. Baseline Calculations
    print("\n[Step 5/7] Calculating competition and player career baselines...")
    comp_baselines = compute_competition_baselines(df_pressure)
    bat_base, bowl_base = compute_player_career_baselines(df_pressure)
    print("  Competition Baselines:\n", comp_baselines[['total_deliveries', 'league_bat_sr', 'league_economy', 'league_dot_pct']])
    
    # 6. Feature Engineering
    print("\n[Step 6/7] Engineering batting and bowling feature datasets...")
    batting_features = engineer_batting_features(df_pressure, bat_base, comp_baselines)
    bowling_features = engineer_bowling_features(df_pressure, bowl_base, comp_baselines)
    
    print(f"  Engineered Batting Dataset: {len(batting_features):,} players")
    print(f"  Engineered Bowling Dataset: {len(bowling_features):,} players")
    
    # 7. Validation & Assertions
    print("\n[Step 7/7] Running validation assertions...")
    
    # Test 1: Zero lookahead leakage
    assert (df_pressure['pre_legal_balls'] <= df_pressure['cum_legal_balls_after']).all(), "Leakage in legal balls!"
    assert (df_pressure['pre_runs'] <= df_pressure['cum_runs_after']).all(), "Leakage in runs!"
    assert (df_pressure['pre_wickets'] <= df_pressure['cum_wickets_after']).all(), "Leakage in wickets!"
    print("  [Pass] Zero lookahead leakage verified.")
    
    # Test 2: Legal balls progression
    assert (df_pressure['rem_legal_balls'] >= 0).all(), "Negative remaining balls detected!"
    assert (df_pressure['wickets_in_hand'] >= 0).all() and (df_pressure['wickets_in_hand'] <= 10).all(), "Invalid wickets in hand!"
    print("  [Pass] Legal balls and wickets progression verified.")
    
    # Test 3: Bowler wickets integrity
    assert set(df_pressure[df_pressure['is_bowler_wicket']]['dismissal_clean'].unique()).issubset(
        {'caught', 'bowled', 'lbw', 'stump', 'hit wicket'}
    ), "Invalid bowler wicket classification!"
    print("  [Pass] Bowler dismissal classification verified.")
    
    # Test 4: Pressure score bounds
    assert (df_pressure['pressure_score'] >= 0.0).all() and (df_pressure['pressure_score'] <= 100.0).all(), "Pressure score out of bounds [0, 100]!"
    print("  [Pass] Pressure score bounds verified [0.0, 100.0].")
    
    # Test 5: Missing dismissed player ID resolved
    assert df_pressure[df_pressure['is_wicket']]['dismissed_player_id'].notnull().all(), "Null dismissed_player_id exists!"
    print("  [Pass] Dismissed player ID completeness verified.")
    
    # Save processed outputs
    print("\nSaving processed datasets to data/processed/...")
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Save deliveries with pressure
    # To keep file size manageable and fast, select key columns for deliveries_with_pressure
    delivery_cols = [
        'match_id', 'innings', 'overid', 'over_ball_num', 'innings_ball_num',
        'comp_category', 'season', 'batting_team_id', 'bowling_team_id',
        'striker_id', 'striker_name', 'bowler_id', 'bowler_name',
        'runs', 'is_four', 'is_six', 'is_wicket', 'dismissal_clean', 'dismissed_player_id',
        'is_legal', 'is_batter_ball', 'is_bowler_wicket', 'bowler_runs_conceded',
        'pre_runs', 'pre_wickets', 'pre_legal_balls', 'wickets_in_hand', 'rem_legal_balls',
        'target', 'runs_needed', 'rrr', 'w_last12', 'w_last18', 'run_deficit', 'wicket_deficit',
        'pressure_score', 'pressure_tier', 'is_pressure_delivery'
    ]
    df_delivery_out = df_pressure[delivery_cols]
    df_delivery_out.to_csv(os.path.join(PROCESSED_DIR, "deliveries_with_pressure.csv"), index=False)
    print(f"  Saved: deliveries_with_pressure.csv ({len(df_delivery_out):,} rows)")
    
    # Save batting features
    batting_features.to_csv(os.path.join(PROCESSED_DIR, "batting_pressure_features.csv"), index=False)
    print(f"  Saved: batting_pressure_features.csv ({len(batting_features):,} players)")
    
    # Save bowling features
    bowling_features.to_csv(os.path.join(PROCESSED_DIR, "bowling_pressure_features.csv"), index=False)
    print(f"  Saved: bowling_pressure_features.csv ({len(bowling_features):,} players)")
    
    # Save competition baselines
    comp_baselines.to_csv(os.path.join(PROCESSED_DIR, "competition_baselines.csv"))
    print("  Saved: competition_baselines.csv")
    
    print("\n" + "=" * 60)
    print("PHASE 2 PROCESSING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    return df_pressure, batting_features, bowling_features, comp_baselines


if __name__ == "__main__":
    run_pipeline()
