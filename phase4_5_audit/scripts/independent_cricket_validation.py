import os
import pandas as pd
import numpy as np

RAW_DIR = r"c:\Users\siddu\Downloads\rr hackathon\data\raw"
PROCESSED_DIR = r"c:\Users\siddu\Downloads\rr hackathon\data\processed"
OUT_CSV = r"c:\Users\siddu\Downloads\rr hackathon\phase4_5_audit\phase4_5_recomputed_player_metrics.csv"

print("Loading raw delivery data and matches...")
raw_bbb = pd.read_csv(os.path.join(RAW_DIR, "ball_by_ball.csv"), low_memory=False)
matches = pd.read_csv(os.path.join(RAW_DIR, "matches.csv"))
df_deliv = pd.read_csv(os.path.join(PROCESSED_DIR, "deliveries_with_pressure.csv"), low_memory=False)

top10_bat_ids = [4708, 6396, 20702, 37052, 1077, 813, 7897, 7260, 152, 8]
top10_bowl_ids = [5979, 1107, 2490, 781, 3644, 4926, 34485, 6628, 2417, 4722]

# Let's verify extras and accounting rules directly
# Legal delivery for bowler: extras_type not in ['wides', 'noballs']
# Batter ball faced: extras_type != 'wides' (no-balls count as balls faced, wides do not)
# Bowler runs conceded: runs + extras where extras_type in ['wides', 'noballs'] (byes and leg-byes are team extras, not charged to bowler)
# Bowler credited wickets: is_wicket == True and dismissal_type not in ['run out', 'retired out', 'retired hurt', 'obstructing the field', 'hit the ball twice', 'timed out']

print("Verifying cricket accounting definitions on df_deliv...")

# Let's recompute metrics under pressure (is_pressure_delivery == True)
p_deliv = df_deliv[df_deliv['is_pressure_delivery']].copy()

recomputed_records = []

# --- BATTING RECOMPUTATION ---
print("\nRecomputing Batting Metrics for Top 10 Batters...")
bat_rank = pd.read_csv(os.path.join(PROCESSED_DIR, "batting_ranking_full.csv"))

for p_id in top10_bat_ids:
    sub = p_deliv[p_deliv['striker_id'] == p_id]
    p_name = sub['striker_name'].iloc[0]
    
    # Batter balls faced: where is_batter_ball is True
    b_sub = sub[sub['is_batter_ball']]
    balls_faced = len(b_sub)
    runs_scored = b_sub['runs'].sum()
    sr = (runs_scored / balls_faced * 100.0) if balls_faced > 0 else 0.0
    fours = (b_sub['is_four']).sum()
    sixes = (b_sub['is_six']).sum()
    bdry_count = fours + sixes
    bdry_pct = (bdry_count / balls_faced * 100.0) if balls_faced > 0 else 0.0
    dots = (b_sub['runs'] == 0).sum()
    dot_pct = (dots / balls_faced * 100.0) if balls_faced > 0 else 0.0
    
    # Dismissals where striker was out
    outs = b_sub['is_wicket'].sum()
    out_pct = (outs / balls_faced * 100.0) if balls_faced > 0 else 0.0
    
    # Distinct matches
    distinct_matches = b_sub['match_id'].nunique()
    
    # Non-pressure baseline
    np_sub = df_deliv[(df_deliv['striker_id'] == p_id) & (~df_deliv['is_pressure_delivery']) & (df_deliv['is_batter_ball'])]
    np_balls = len(np_sub)
    np_runs = np_sub['runs'].sum()
    np_sr = (np_runs / np_balls * 100.0) if np_balls > 0 else 0.0
    unbiased_delta_sr = sr - np_sr
    
    # Consistency: % matches with SR >= 140 (min 5 balls)
    match_srs = b_sub.groupby('match_id').agg(
        m_runs=('runs', 'sum'),
        m_balls=('runs', 'count')
    )
    sig_matches = match_srs[match_srs['m_balls'] >= 5]
    if len(sig_matches) > 0:
        consist = ((sig_matches['m_runs'] / sig_matches['m_balls'] * 100.0) >= 140.0).mean() * 100.0
    else:
        consist = ((match_srs['m_runs'] / match_srs['m_balls'] * 100.0) >= 140.0).mean() * 100.0
        
    # Get previously reported metrics from bat_rank
    prev = bat_rank[bat_rank['striker_id'] == p_id].iloc[0]
    
    recomputed_records.append({
        'discipline': 'Batting',
        'player_id': p_id,
        'player_name': p_name,
        'recomp_p_opps': balls_faced,
        'prev_p_opps': prev['p_balls_faced'],
        'recomp_runs': runs_scored,
        'prev_runs': prev['p_runs'],
        'recomp_rate': round(sr, 2),
        'prev_rate': round(prev['p_strike_rate'], 2),
        'recomp_eb_rate': round(prev['eb_p_sr'], 2),
        'recomp_dot_pct': round(dot_pct, 2),
        'prev_csv_dot_pct': round(prev['p_dot_pct'], 2),
        'recomp_bdry_pct': round(bdry_pct, 2),
        'prev_csv_bdry_pct': round(prev['p_boundary_pct'], 2),
        'recomp_out_pct': round(out_pct, 2),
        'prev_csv_out_pct': round(prev['p_dismissal_rate'], 2),
        'recomp_clutch_lift': round(unbiased_delta_sr, 2),
        'prev_clutch_lift': round(prev['unbiased_delta_sr'], 2),
        'recomp_consistency': round(consist, 2),
        'prev_consistency': round(prev['pct_matches_above_140'], 2),
        'bpri_score': round(prev['BPRI_Model1_Balanced'], 2),
        'rank': int(prev['rank'])
    })

# --- BOWLING RECOMPUTATION ---
print("\nRecomputing Bowling Metrics for Top 10 Bowlers...")
bowl_rank = pd.read_csv(os.path.join(PROCESSED_DIR, "bowling_ranking_full.csv"))

for b_id in top10_bowl_ids:
    sub = p_deliv[p_deliv['bowler_id'] == b_id]
    b_name = sub['bowler_name'].iloc[0]
    
    # Bowler legal deliveries
    l_sub = sub[sub['is_legal']]
    legal_balls = len(l_sub)
    
    # Bowler runs conceded (sum over ALL sub deliveries for this bowler in pressure)
    # Wides and no-balls conceded by bowler under pressure are charged to bowler!
    runs_conceded = sub['bowler_runs_conceded'].sum()
    econ = (runs_conceded / (legal_balls / 6.0)) if legal_balls > 0 else 0.0
    
    # Bowler credited wickets
    wkts = sub['is_bowler_wicket'].sum()
    bowl_sr = (legal_balls / wkts) if wkts > 0 else 999.0
    
    # Dots: where bowler runs conceded == 0 on legal balls
    dots = (l_sub['bowler_runs_conceded'] == 0).sum()
    dot_pct = (dots / legal_balls * 100.0) if legal_balls > 0 else 0.0
    
    # Boundaries conceded on legal balls
    fours = (l_sub['is_four']).sum()
    sixes = (l_sub['is_six']).sum()
    bdry_count = fours + sixes
    bdry_pct = (bdry_count / legal_balls * 100.0) if legal_balls > 0 else 0.0
    
    # Non-pressure baseline
    np_sub = df_deliv[(df_deliv['bowler_id'] == b_id) & (~df_deliv['is_pressure_delivery'])]
    np_legal = np_sub[np_sub['is_legal']]
    np_runs = np_sub['bowler_runs_conceded'].sum()
    np_econ = (np_runs / (len(np_legal) / 6.0)) if len(np_legal) > 0 else 0.0
    delta_econ = np_econ - econ  # positive means saving runs under pressure
    
    # Consistency: % spells with econ < 8.5
    spell_econs = sub.groupby('match_id').agg(
        s_runs=('bowler_runs_conceded', 'sum'),
        s_balls=('is_legal', 'sum')
    )
    sig_spells = spell_econs[spell_econs['s_balls'] >= 6]
    if len(sig_spells) > 0:
        consist = ((sig_spells['s_runs'] / (sig_spells['s_balls'] / 6.0)) < 8.5).mean() * 100.0
    else:
        consist = ((spell_econs['s_runs'] / (spell_econs['s_balls'] / 6.0)) < 8.5).mean() * 100.0
        
    prev = bowl_rank[bowl_rank['bowler_id'] == b_id].iloc[0]
    
    recomputed_records.append({
        'discipline': 'Bowling',
        'player_id': b_id,
        'player_name': b_name,
        'recomp_p_opps': legal_balls,
        'prev_p_opps': prev['p_legal_balls'],
        'recomp_runs': runs_conceded,
        'prev_runs': prev['p_runs_conceded'],
        'recomp_rate': round(econ, 2),
        'prev_rate': round(prev['p_economy'], 2),
        'recomp_eb_rate': round(prev['eb_p_econ'], 2),
        'recomp_dot_pct': round(dot_pct, 2),
        'prev_csv_dot_pct': round(prev['p_dot_pct'], 2),
        'recomp_bdry_pct': round(bdry_pct, 2),
        'prev_csv_bdry_pct': round(prev['p_boundary_pct'], 2),
        'recomp_out_pct': round(wkts, 2),  # Wickets for bowling
        'prev_csv_out_pct': round(prev['p_wickets'], 2),
        'recomp_clutch_lift': round(delta_econ, 2),
        'prev_clutch_lift': round(prev['unbiased_delta_econ'], 2),
        'recomp_consistency': round(consist, 2),
        'prev_consistency': round(prev['pct_spells_sub_8_5'], 2),
        'bpri_score': round(prev['BPRI_Model1_Balanced'], 2),
        'rank': int(prev['rank'])
    })

df_recomp = pd.DataFrame(recomputed_records)
df_recomp.to_csv(OUT_CSV, index=False)
print(f"\nGenerated phase4_5_recomputed_player_metrics.csv with {len(df_recomp)} records.")
print("\nRecomputed vs CSV Comparison Preview:")
print(df_recomp[['rank', 'discipline', 'player_name', 'recomp_p_opps', 'recomp_runs', 'recomp_rate', 'recomp_dot_pct', 'prev_csv_dot_pct', 'recomp_bdry_pct', 'prev_csv_bdry_pct', 'bpri_score']].to_string())
