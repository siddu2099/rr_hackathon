"""
pressure_model.py
Continuous pressure calculation and discrete tier classification module.
Provides interpretable, mathematically justified, leakage-free pressure metrics.
Audited for Phase 3:
1. Strict theoretical bounds [0, 100] without artificial clipping.
2. Continuous, smooth chasing leverage curve (zero piecewise discontinuities).
3. Non-overlapping collapse shock and structural wicket deficit in 1st innings.
"""

import numpy as np
import pandas as pd


def calc_continuous_leverage(b_rem, rrr=10.0):
    """
    Computes smooth, monotonic delivery leverage in chasing (Innings 2).
    Ramps continuously from 0 at 60 remaining balls to 25.0 at 0 remaining balls.
    Applies contest closeness / blowout dampener if match is out of hand (RRR > 20.0).
    """
    if b_rem >= 60.0 or pd.isna(b_rem):
        return 0.0
    x = (60.0 - b_rem) / 60.0 # Exactly in [0.0, 1.0]
    
    # Contest closeness multiplier
    if 6.0 <= rrr <= 20.0:
        closeness = 1.0
    elif rrr < 6.0:
        closeness = max(0.2, rrr / 6.0) # low target cruise
    else: # rrr > 20.0: blowout dampener
        closeness = max(0.1, 1.0 - (rrr - 20.0) / 15.0)
        
    return float(x * 25.0 * closeness)


def calc_inn2_pressure_row(row):
    """
    Computes second-innings chasing pressure score in [0, 100].
    Strictly bounded: Demand [0, 50] + Wicket [0, 25] + Leverage [0, 25] = [0, 100].
    """
    rrr = row['rrr']
    b_rem = row['rem_legal_balls']
    w_rem = row['wickets_in_hand']
    r_rem = row['runs_needed']
    
    if pd.isna(rrr) or b_rem <= 0 or r_rem <= 0:
        return 0.0
        
    # 1. Demand score: RRR relative to baseline 8.5 [0, 50]
    # RRR <= 6 -> 0; RRR 8.5 -> 10.4; RRR 12 -> 25.0; RRR 15 -> 37.5; RRR >= 18 -> 50.0
    d_score = np.clip((rrr - 6.0) / 12.0, 0.0, 1.0) * 50.0
    
    # 2. Wicket pressure score [0, 25]
    # 10 wickets -> 0; 7 wickets -> 6.25; 4 wickets -> 15.6; 1 wicket -> 25.0
    w_score = np.clip((9.0 - w_rem) / 8.0, 0.0, 1.0) * 25.0
    
    # 3. Continuous leverage / finish closeness [0, 25]
    l_score = calc_continuous_leverage(b_rem, rrr)
    
    total_p = d_score + w_score + l_score
    return float(np.clip(total_p, 0.0, 100.0))


def calc_inn1_pressure_row(row):
    """
    Computes first-innings pressure score in [0, 100].
    Strictly bounded: Acute Collapse [0, 30] + Structural Wickets [0, 30] + Run Deficit [0, 25] + Death [0, 15] = [0, 100].
    """
    b_rem = row['rem_legal_balls']
    b_elapsed = row['pre_legal_balls']
    w_rem = row['wickets_in_hand']
    w_lost = row['pre_wickets']
    w_l12 = row['w_last12']
    run_def = row['run_deficit']
    w_def = row['wicket_deficit']
    
    # 1. Acute collapse shock [0, 30]
    # Recent wicket cluster in last 12 legal balls
    if w_l12 >= 3:
        collapse_score = 30.0
    elif w_l12 == 2:
        collapse_score = 20.0
    elif w_l12 == 1:
        collapse_score = 5.0
    else:
        collapse_score = 0.0
        
    # 2. Structural Wicket Deficit [0, 30]
    # Excess wickets down relative to expected par progression
    # Extra preservation stress if <= 3 wickets in hand
    w_score = np.clip(w_def / 3.0, 0.0, 1.0) * 20.0
    if w_rem <= 3:
        w_score += 10.0
    elif b_elapsed <= 36 and w_lost >= 3: # early powerplay collapse
        w_score += 10.0
    w_score = min(30.0, w_score)
        
    # 3. Run deficit component [0, 25]
    r_score = np.clip(run_def / 25.0, 0.0, 1.0) * 25.0
    
    # 4. Death overs acceleration leverage [0, 15]
    if b_rem <= 30:
        death_factor = (30.0 - b_rem) / 30.0
        d_score = death_factor * (15.0 if w_rem <= 5 else 8.0)
    else:
        d_score = 0.0
        
    total_p = collapse_score + w_score + r_score + d_score
    return float(np.clip(total_p, 0.0, 100.0))


def apply_pressure_model(df):
    """
    Applies the audited pressure model across all deliveries.
    Returns dataframe with pressure_score, pressure_tier, and is_pressure_delivery.
    """
    df_out = df.copy()
    
    inn1_mask = df_out['innings'] == 1
    inn2_mask = df_out['innings'] == 2
    super_mask = df_out['innings'] > 2
    
    scores = np.zeros(len(df_out), dtype=float)
    
    inn1_scores = df_out[inn1_mask].apply(calc_inn1_pressure_row, axis=1).values
    scores[inn1_mask] = inn1_scores
    
    inn2_scores = df_out[inn2_mask].apply(calc_inn2_pressure_row, axis=1).values
    scores[inn2_mask] = inn2_scores
    
    # Super overs: maximum pressure (100.0)
    scores[super_mask] = 100.0
    
    df_out['pressure_score'] = scores
    
    # Discrete Tiers:
    # Low: [0, 20)
    # Moderate: [20, 45)
    # High: [45, 70)
    # Critical: [70, 100]
    conditions = [
        df_out['pressure_score'] < 20.0,
        (df_out['pressure_score'] >= 20.0) & (df_out['pressure_score'] < 45.0),
        (df_out['pressure_score'] >= 45.0) & (df_out['pressure_score'] < 70.0),
        df_out['pressure_score'] >= 70.0
    ]
    choices = ['Low', 'Moderate', 'High', 'Critical']
    df_out['pressure_tier'] = np.select(conditions, choices, default='Low')
    
    # High Pressure definition: High and Critical tiers combined (P >= 45.0)
    df_out['is_pressure_delivery'] = df_out['pressure_score'] >= 45.0
    
    return df_out
