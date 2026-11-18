"""
match_state.py
Pre-delivery match-state reconstruction module.
Guarantees zero data leakage by computing all state variables strictly prior to each delivery.
"""

import numpy as np
import pandas as pd


def clean_delivery_metadata(df_bbb):
    """
    Standardize text labels for extras and dismissals, and classify legal balls.
    """
    df = df_bbb.copy()
    
    # 1. Clean extras type
    df['extras_type_clean'] = df['extras_type'].astype(str).str.lower().replace({'nan': 'none', 'none': 'none'})
    df['is_wide'] = df['extras_type_clean'] == 'wide'
    df['is_noball'] = df['extras_type_clean'].isin(['overstep', 'other'])
    df['is_bye_legbye'] = df['extras_type_clean'].isin(['byes', 'legbyes'])
    
    # In cricket, legal deliveries count towards the 6-ball over.
    # Wides and no-balls are NOT legal deliveries.
    df['is_legal'] = ~df['is_wide'] & ~df['is_noball']
    
    # For batters, balls faced includes legal balls and no-balls, but NOT wides.
    df['is_batter_ball'] = ~df['is_wide']
    
    # 2. Clean dismissal type and bowler credit
    bowler_wicket_types = {'caught', 'bowled', 'lbw', 'stump', 'hit wicket'}
    df['dismissal_clean'] = df['dismissal_type'].astype(str).str.lower().replace({'nan': 'none', 'none': 'none'})
    # Fix typo 'obstracting the field'
    df['dismissal_clean'] = df['dismissal_clean'].replace({'obstracting the field': 'obstructing the field'})
    
    # Bowler credited wickets
    df['is_bowler_wicket'] = df['is_wicket'] & df['dismissal_clean'].isin(bowler_wicket_types)
    
    # Impute missing dismissed_player_id on Retire Out (e.g. Hardik Pandya row 127899)
    retire_mask = df['is_wicket'] & df['dismissed_player_id'].isna() & (df['dismissal_clean'] == 'retire out')
    df.loc[retire_mask, 'dismissed_player_id'] = df.loc[retire_mask, 'striker_id']
    
    # 3. Calculate team runs on delivery
    df['total_ball_runs'] = df['runs'] + df['extras1_runs'] + df['extras_2_runs']
    
    # 4. Calculate bowler runs conceded on delivery
    # Wides: extras1_runs
    # No-balls (overstep/other): extras1_runs + runs off bat (extras_2_runs are byes/legbyes, not bowler runs)
    # Byes/legbyes/penalty: 0
    # Clean balls: runs
    def calc_bowler_runs(row):
        et = row['extras_type_clean']
        if et == 'wide':
            return row['extras1_runs']
        elif et in ('overstep', 'other'):
            return row['extras1_runs'] + row['runs']
        elif et in ('byes', 'legbyes', 'penalty'):
            return 0
        else:
            return row['runs']
            
    df['bowler_runs_conceded'] = df.apply(calc_bowler_runs, axis=1)
    
    return df


def reconstruct_pre_delivery_state(df_clean, df_matches):
    """
    Chronologically reconstruct cumulative match state and shift by 1 delivery
    to guarantee zero lookahead leakage.
    """
    df = df_clean.sort_values(by=['match_id', 'innings', 'innings_ball_num']).reset_index(drop=True)
    
    # Cumulative states AFTER delivery
    df['cum_runs_after'] = df.groupby(['match_id', 'innings'])['total_ball_runs'].cumsum()
    df['cum_wickets_after'] = df.groupby(['match_id', 'innings'])['is_wicket'].cumsum()
    df['cum_legal_balls_after'] = df.groupby(['match_id', 'innings'])['is_legal'].cumsum()
    
    # Pre-delivery state: shift by 1 delivery per innings
    df['pre_runs'] = df.groupby(['match_id', 'innings'])['cum_runs_after'].shift(1).fillna(0).astype(int)
    df['pre_wickets'] = df.groupby(['match_id', 'innings'])['cum_wickets_after'].shift(1).fillna(0).astype(int)
    df['pre_legal_balls'] = df.groupby(['match_id', 'innings'])['cum_legal_balls_after'].shift(1).fillna(0).astype(int)
    
    # Wickets in hand
    df['wickets_in_hand'] = (10 - df['pre_wickets']).clip(lower=0)
    
    # Match metadata lookup
    meta_dict = df_matches.set_index('match_id')[
        ['revised_target', 'second_inn_revised_overs', 'first_inn_revised_overs', 'knock_out', 'comp_id']
    ].to_dict('index')
    
    # Total 1st innings scores
    inn1_totals = df[df['innings'] == 1].groupby('match_id')['cum_runs_after'].max().to_dict()
    
    # Assign target for 2nd innings
    def get_target(row):
        if row['innings'] == 2:
            m_id = row['match_id']
            meta = meta_dict.get(m_id, {})
            rev_t = meta.get('revised_target')
            if pd.notnull(rev_t) and rev_t > 0:
                return float(rev_t)
            t1 = inn1_totals.get(m_id)
            if t1 is not None:
                return float(t1 + 1)
        return np.nan
        
    df['target'] = df.apply(get_target, axis=1)
    
    # Total scheduled legal balls
    def get_total_legal_balls(row):
        m_id = row['match_id']
        meta = meta_dict.get(m_id, {})
        if row['innings'] == 1:
            rev_o = meta.get('first_inn_revised_overs')
            if pd.notnull(rev_o) and rev_o > 0:
                return int(rev_o * 6)
            return 120
        elif row['innings'] == 2:
            rev_o = meta.get('second_inn_revised_overs')
            if pd.notnull(rev_o) and rev_o > 0:
                return int(rev_o * 6)
            return 120
        else:
            return 6 # Super Over
            
    df['total_legal_balls'] = df.apply(get_total_legal_balls, axis=1)
    df['rem_legal_balls'] = (df['total_legal_balls'] - df['pre_legal_balls']).clip(lower=0)
    
    # Chasing metrics (Innings 2)
    df['runs_needed'] = np.where(df['innings'] == 2, (df['target'] - df['pre_runs']).clip(lower=0), np.nan)
    df['rrr'] = np.where(
        (df['innings'] == 2) & (df['rem_legal_balls'] > 0),
        df['runs_needed'] / (df['rem_legal_balls'] / 6.0),
        np.nan
    )
    
    # Current Run Rate (CRR)
    df['crr'] = np.where(
        df['pre_legal_balls'] > 0,
        df['pre_runs'] / (df['pre_legal_balls'] / 6.0),
        0.0
    )
    
    # Batting collapse features: rolling wickets in previous 12 and 18 legal deliveries
    df = add_rolling_collapse_features(df)
    
    # First innings par trajectory
    df = add_par_trajectory_features(df)
    
    return df


def add_rolling_collapse_features(df):
    """
    Computes wickets lost in previous 12 and 18 legal deliveries without lookahead.
    Uses rolling two-pointer algorithm on legal ball indices.
    """
    def _calc_recent(group):
        legal_balls = group['pre_legal_balls'].values
        cum_w = group['pre_wickets'].values
        n = len(group)
        w_l12 = np.zeros(n, dtype=int)
        w_l18 = np.zeros(n, dtype=int)
        
        idx_12 = 0
        idx_18 = 0
        for i in range(n):
            l_curr = legal_balls[i]
            while idx_12 < i and legal_balls[idx_12] < l_curr - 12:
                idx_12 += 1
            while idx_18 < i and legal_balls[idx_18] < l_curr - 18:
                idx_18 += 1
            w_l12[i] = cum_w[i] - cum_w[idx_12]
            w_l18[i] = cum_w[i] - cum_w[idx_18]
            
        group['w_last12'] = w_l12
        group['w_last18'] = w_l18
        return group

    return df.groupby(['match_id', 'innings'], group_keys=False).apply(_calc_recent)


def add_par_trajectory_features(df):
    """
    Computes empirical par score and par wickets at each legal ball of Innings 1.
    """
    normal_inn1 = df[(df['innings'] == 1) & (df['total_legal_balls'] == 120)]
    par_runs_map = normal_inn1.groupby('pre_legal_balls')['pre_runs'].mean().to_dict()
    par_w_map = normal_inn1.groupby('pre_legal_balls')['pre_wickets'].mean().to_dict()
    
    df['par_runs'] = df['pre_legal_balls'].map(par_runs_map).fillna(0.0)
    df['run_deficit'] = df['par_runs'] - df['pre_runs']
    
    df['par_wickets'] = df['pre_legal_balls'].map(par_w_map).fillna(0.0)
    df['wicket_deficit'] = df['pre_wickets'] - df['par_wickets']
    
    return df
