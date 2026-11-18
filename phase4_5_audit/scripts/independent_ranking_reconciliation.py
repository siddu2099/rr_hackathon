import os
import pandas as pd
import numpy as np

PROCESSED_DIR = r"c:\Users\siddu\Downloads\rr hackathon\data\processed"
OUT_CSV = r"c:\Users\siddu\Downloads\rr hackathon\phase4_5_audit\phase4_5_ranking_reconciliation.csv"

bat_rank = pd.read_csv(os.path.join(PROCESSED_DIR, "batting_ranking_full.csv"))
bowl_rank = pd.read_csv(os.path.join(PROCESSED_DIR, "bowling_ranking_full.csv"))

# Compute No-Volume BPRI for Batters
bat_rank['bpri_no_vol'] = (
    (0.25 * bat_rank['norm_eb_sr'] +
     0.05 * bat_rank['norm_boundary'] +
     0.05 * bat_rank['norm_dot'] +
     0.25 * bat_rank['norm_delta_sr'] +
     0.15 * bat_rank['norm_consistency'] +
     0.10 * bat_rank['norm_dismissal']) / 0.85
).round(2)

bat_rank['rank_bal'] = bat_rank['BPRI_Model1_Balanced'].rank(ascending=False, method='min').astype(int)
bat_rank['rank_novol'] = bat_rank['bpri_no_vol'].rank(ascending=False, method='min').astype(int)
bat_rank['rank_exec'] = bat_rank['BPRI_Model3_Absolute'].rank(ascending=False, method='min').astype(int)
bat_rank['rank_clutch'] = bat_rank['BPRI_Model2_ClutchLift'].rank(ascending=False, method='min').astype(int)

# Compute No-Volume BPRI for Bowlers
bowl_rank['bpri_no_vol'] = (
    (0.25 * bowl_rank['norm_eb_econ'] +
     0.05 * bowl_rank['norm_dot'] +
     0.05 * bowl_rank['norm_boundary'] +
     0.25 * bowl_rank['norm_bowl_sr'] +
     0.20 * bowl_rank['norm_delta_econ'] +
     0.10 * bowl_rank['norm_consistency']) / 0.90
).round(2)

bowl_rank['rank_bal'] = bowl_rank['BPRI_Model1_Balanced'].rank(ascending=False, method='min').astype(int)
bowl_rank['rank_novol'] = bowl_rank['bpri_no_vol'].rank(ascending=False, method='min').astype(int)
bowl_rank['rank_wickets'] = bowl_rank['BPRI_Model2_Wickets'].rank(ascending=False, method='min').astype(int)
bowl_rank['rank_econ'] = bowl_rank['BPRI_Model3_Economy'].rank(ascending=False, method='min').astype(int)

reconcil_records = []

# Top 10 Batters reconciliation
top10_bat = bat_rank.sort_values(by='rank_bal').head(10)
for idx, r in top10_bat.iterrows():
    reconcil_records.append({
        'discipline': 'Batting',
        'player_id': r['striker_id'],
        'player_name': r['striker_name'],
        'p_opportunities': r['p_balls_faced'],
        'balanced_rank': r['rank_bal'],
        'balanced_score': r['BPRI_Model1_Balanced'],
        'no_vol_rank': r['rank_novol'],
        'no_vol_score': r['bpri_no_vol'],
        'rank_shift_no_vol': r['rank_novol'] - r['rank_bal'],
        'model2_rank': r['rank_clutch'],
        'model3_rank': r['rank_exec'],
        'in_top10_no_vol': bool(r['rank_novol'] <= 10)
    })

# Top 10 Bowlers reconciliation
top10_bowl = bowl_rank.sort_values(by='rank_bal').head(10)
for idx, r in top10_bowl.iterrows():
    reconcil_records.append({
        'discipline': 'Bowling',
        'player_id': r['bowler_id'],
        'player_name': r['bowler_name'],
        'p_opportunities': r['p_legal_balls'],
        'balanced_rank': r['rank_bal'],
        'balanced_score': r['BPRI_Model1_Balanced'],
        'no_vol_rank': r['rank_novol'],
        'no_vol_score': r['bpri_no_vol'],
        'rank_shift_no_vol': r['rank_novol'] - r['rank_bal'],
        'model2_rank': r['rank_wickets'],
        'model3_rank': r['rank_econ'],
        'in_top10_no_vol': bool(r['rank_novol'] <= 10)
    })

df_reconcil = pd.DataFrame(reconcil_records)
df_reconcil.to_csv(OUT_CSV, index=False)
print(f"Generated phase4_5_ranking_reconciliation.csv with {len(df_reconcil)} records.")
print("\nRanking Reconciliation Preview:")
print(df_reconcil[['discipline', 'player_name', 'p_opportunities', 'balanced_rank', 'no_vol_rank', 'rank_shift_no_vol', 'in_top10_no_vol', 'model2_rank', 'model3_rank']].to_string())
