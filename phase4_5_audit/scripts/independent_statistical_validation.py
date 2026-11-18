import os
import pandas as pd
import numpy as np
from scipy import stats

PROCESSED_DIR = r"c:\Users\siddu\Downloads\rr hackathon\data\processed"
OUT_CSV = r"c:\Users\siddu\Downloads\rr hackathon\phase4_5_audit\phase4_5_statistical_validation.csv"

print("Loading data for statistical validation...")
df_deliv = pd.read_csv(os.path.join(PROCESSED_DIR, "deliveries_with_pressure.csv"), low_memory=False)
top_bat = pd.read_csv(os.path.join(PROCESSED_DIR, "top10_batters.csv"))
top_bowl = pd.read_csv(os.path.join(PROCESSED_DIR, "top10_bowlers.csv"))

np.random.seed(42)

# Prior parameters from Phase 3
PRIOR_BAT_MU = 136.07
PRIOR_BAT_N0 = 28.64  # sigma^2 / tau^2 = 3681.44 / 128.53 = 28.64
PRIOR_BAT_SIGMA = 60.67

PRIOR_BOWL_MU = 8.33
PRIOR_BOWL_B0 = 33.82

stat_records = []

# --- 1. BATTING BOOTSTRAP (10,000 iterations) ---
print("\nRunning 10,000-iteration Match-Cluster Bootstrap for Top 10 Batters...")
p_bat_deliv = df_deliv[df_deliv['is_pressure_delivery'] & df_deliv['is_batter_ball']].copy()

# Pre-aggregate by player and match for sub-second 10k bootstrap speed
bat_match_agg = p_bat_deliv.groupby(['striker_id', 'match_id']).agg(
    runs=('runs', 'sum'),
    balls=('runs', 'count')
).reset_index()

n_boot = 10000

for idx, r in top_bat.iterrows():
    p_id = r['striker_id']
    p_name = r['striker_name']
    p_matches = bat_match_agg[bat_match_agg['striker_id'] == p_id]
    m_runs = p_matches['runs'].values
    m_balls = p_matches['balls'].values
    n_m = len(m_runs)
    
    # 10k bootstrap replicates
    boot_indices = np.random.randint(0, n_m, size=(n_boot, n_m))
    boot_sample_runs = np.take(m_runs, boot_indices).sum(axis=1)
    boot_sample_balls = np.take(m_balls, boot_indices).sum(axis=1)
    
    # Avoid div by zero
    valid = boot_sample_balls > 0
    boot_srs = (boot_sample_runs[valid] / boot_sample_balls[valid]) * 100.0
    
    boot_mean = float(np.mean(boot_srs))
    boot_se = float(np.std(boot_srs))
    boot_ci_low = float(np.percentile(boot_srs, 2.5))
    boot_ci_high = float(np.percentile(boot_srs, 97.5))
    
    # Empirical Bayes Posterior
    n_i = r['p_balls_faced']
    w_i = n_i / (n_i + PRIOR_BAT_N0)
    eb_mean = w_i * r['p_strike_rate'] + (1 - w_i) * PRIOR_BAT_MU
    
    # Bayesian Credible Interval under Normal-Normal
    post_var = 1.0 / (1.0 / 128.53 + n_i / (PRIOR_BAT_SIGMA ** 2))
    post_sd = np.sqrt(post_var)
    bayes_ci_low = eb_mean - 1.96 * post_sd
    bayes_ci_high = eb_mean + 1.96 * post_sd
    
    # Statistical significance against league average finisher (Wald test)
    z_score = (boot_mean - PRIOR_BAT_MU) / boot_se
    # Two-sided p-value
    raw_p_value = float(2 * (1 - stats.norm.cdf(abs(z_score))))
    # Bonferroni adjusted for 153 eligible batters
    bonf_p_value = min(1.0, raw_p_value * 153)
    
    stat_records.append({
        'discipline': 'Batting',
        'player_id': p_id,
        'player_name': p_name,
        'sample_size': n_i,
        'matches': n_m,
        'raw_metric': r['p_strike_rate'],
        'eb_mean': round(eb_mean, 2),
        'eb_weight': round(w_i, 3),
        'bayes_95ci_low': round(bayes_ci_low, 2),
        'bayes_95ci_high': round(bayes_ci_high, 2),
        'boot_10k_mean': round(boot_mean, 2),
        'boot_10k_se': round(boot_se, 2),
        'boot_95ci_low': round(boot_ci_low, 2),
        'boot_95ci_high': round(boot_ci_high, 2),
        'null_hypothesis_value': PRIOR_BAT_MU,
        'wald_z_score': round(z_score, 2),
        'raw_p_value': f"{raw_p_value:.2e}" if raw_p_value < 0.0001 else f"{raw_p_value:.4f}",
        'bonferroni_p_value': f"{bonf_p_value:.2e}" if bonf_p_value < 0.0001 else f"{bonf_p_value:.4f}",
        'statistically_significant_001': bool(bonf_p_value < 0.001)
    })

# --- 2. BOWLING BOOTSTRAP (10,000 iterations) ---
print("\nRunning 10,000-iteration Match-Cluster Bootstrap for Top 10 Bowlers...")
p_bowl_deliv = df_deliv[df_deliv['is_pressure_delivery']].copy()

bowl_match_agg = p_bowl_deliv.groupby(['bowler_id', 'match_id']).agg(
    runs=('bowler_runs_conceded', 'sum'),
    legal_balls=('is_legal', 'sum')
).reset_index()

for idx, r in top_bowl.iterrows():
    b_id = r['bowler_id']
    b_name = r['bowler_name']
    b_matches = bowl_match_agg[bowl_match_agg['bowler_id'] == b_id]
    m_runs = b_matches['runs'].values
    m_balls = b_matches['legal_balls'].values
    n_m = len(m_runs)
    
    boot_indices = np.random.randint(0, n_m, size=(n_boot, n_m))
    boot_sample_runs = np.take(m_runs, boot_indices).sum(axis=1)
    boot_sample_balls = np.take(m_balls, boot_indices).sum(axis=1)
    
    valid = boot_sample_balls > 0
    boot_econs = (boot_sample_runs[valid] / (boot_sample_balls[valid] / 6.0))
    
    boot_mean = float(np.mean(boot_econs))
    boot_se = float(np.std(boot_econs))
    boot_ci_low = float(np.percentile(boot_econs, 2.5))
    boot_ci_high = float(np.percentile(boot_econs, 97.5))
    
    # Empirical Bayes Posterior
    b_i = r['p_legal_balls']
    w_i = b_i / (b_i + PRIOR_BOWL_B0)
    eb_mean = w_i * r['p_economy'] + (1 - w_i) * PRIOR_BOWL_MU
    
    # Bayesian Credible Interval
    post_var = 1.0 / (1.0 / 2.37 + b_i / (3.18 ** 2))
    post_sd = np.sqrt(post_var)
    bayes_ci_low = eb_mean - 1.96 * post_sd
    bayes_ci_high = eb_mean + 1.96 * post_sd
    
    # Statistical significance against league average bowler (Wald test: econ < 8.33)
    z_score = (PRIOR_BOWL_MU - boot_mean) / boot_se  # positive means significantly lower economy
    raw_p_value = float(2 * (1 - stats.norm.cdf(abs(z_score))))
    bonf_p_value = min(1.0, raw_p_value * 133)
    
    stat_records.append({
        'discipline': 'Bowling',
        'player_id': b_id,
        'player_name': b_name,
        'sample_size': b_i,
        'matches': n_m,
        'raw_metric': r['p_economy'],
        'eb_mean': round(eb_mean, 2),
        'eb_weight': round(w_i, 3),
        'bayes_95ci_low': round(bayes_ci_low, 2),
        'bayes_95ci_high': round(bayes_ci_high, 2),
        'boot_10k_mean': round(boot_mean, 2),
        'boot_10k_se': round(boot_se, 2),
        'boot_95ci_low': round(boot_ci_low, 2),
        'boot_95ci_high': round(boot_ci_high, 2),
        'null_hypothesis_value': PRIOR_BOWL_MU,
        'wald_z_score': round(z_score, 2),
        'raw_p_value': f"{raw_p_value:.2e}" if raw_p_value < 0.0001 else f"{raw_p_value:.4f}",
        'bonferroni_p_value': f"{bonf_p_value:.2e}" if bonf_p_value < 0.0001 else f"{bonf_p_value:.4f}",
        'statistically_significant_001': bool(bonf_p_value < 0.001)
    })

df_stat = pd.DataFrame(stat_records)
df_stat.to_csv(OUT_CSV, index=False)
print(f"\nGenerated phase4_5_statistical_validation.csv with {len(df_stat)} records.")
print("\nStatistical Validation Preview:")
print(df_stat[['player_name', 'discipline', 'raw_metric', 'eb_mean', 'boot_10k_mean', 'boot_10k_se', 'boot_95ci_low', 'boot_95ci_high', 'wald_z_score', 'bonferroni_p_value', 'statistically_significant_001']].to_string())
