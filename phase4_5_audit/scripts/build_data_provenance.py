import os
import hashlib
import pandas as pd
from datetime import datetime

BASE_DIR = r"c:\Users\siddu\Downloads\rr hackathon"
BRAIN_DIR = r"C:\Users\siddu\.gemini\antigravity\brain\712fc9c2-3466-4850-b1b0-13da6452bcd0"
OUT_CSV = os.path.join(BASE_DIR, "phase4_5_audit", "phase4_5_data_provenance.csv")

def sha256_file(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_purpose_and_deps(filename, rel_path):
    fn = filename.lower()
    if 'raw' in rel_path or fn in ['ball_by_ball.csv', 'matches.csv', 'competitions.csv', 'teams.csv', 'playing_eleven.csv', 'competition_team_player_mapping.csv']:
        return "Raw untouched tournament dataset provided by organizers", "None (Primary Source)"
    elif 'deliveries_with_pressure' in fn:
        return "Delivery-level match state and continuous pressure classification dataset", "data/raw/ball_by_ball.csv, matches.csv, src/match_state.py, src/pressure_model.py"
    elif 'batting_pressure_features' in fn:
        return "Aggregated batter features under pressure and career baselines", "data/processed/deliveries_with_pressure.csv, src/batting_features.py"
    elif 'bowling_pressure_features' in fn:
        return "Aggregated bowler features under pressure and career baselines", "data/processed/deliveries_with_pressure.csv, src/bowling_features.py"
    elif 'batting_ranking_full' in fn or 'top10_batters' in fn:
        return "Full and top 10 batting rankings evaluated across BPRI models", "batting_pressure_features.csv, src/ranking_models.py"
    elif 'bowling_ranking_full' in fn or 'top10_bowlers' in fn:
        return "Full and top 10 bowling rankings evaluated across BPRI_bowl models", "bowling_pressure_features.csv, src/ranking_models.py"
    elif 'phase4_final_validated_rankings' in fn:
        return "Final combined Top 10 validated batters and bowlers ladder with bootstrap CIs", "top10_batters.csv, top10_bowlers.csv, ranking_sensitivity.csv"
    elif 'phase4_sensitivity_results' in fn or 'ranking_sensitivity' in fn:
        return "Ranking sensitivity analysis across thresholds, cutoffs, and weighting models", "src/ranking_models.py, pipeline outputs"
    elif 'competition_baselines' in fn:
        return "Scoring baselines aggregated by competition tier and match phase", "deliveries_with_pressure.csv, src/baselines.py"
    elif fn.endswith('.png'):
        return "Publication-grade statistical visualization artifact", "data/processed/ datasets, matplotlib/seaborn scripts"
    elif fn.endswith('.py'):
        if 'src' in rel_path:
            return "Production pipeline and ranking model script", "pandas, numpy, scipy"
        elif 'phase4_5' in rel_path:
            return "Independent validation and audit script", "data/raw/, data/processed/"
        else:
            return "Scratch diagnostic or visualization script", "data/processed/"
    elif fn.endswith('.md'):
        return "Analytical report / documentation artifact", "Pipeline and audit outputs"
    else:
        return "General project asset / documentation", "None"

records = []
scan_dirs = [
    (os.path.join(BASE_DIR, "data", "raw"), "data/raw"),
    (os.path.join(BASE_DIR, "data", "processed"), "data/processed"),
    (os.path.join(BASE_DIR, "src"), "src"),
    (os.path.join(BASE_DIR, "phase4_visualizations"), "phase4_visualizations"),
    (BASE_DIR, "root"),
    (BRAIN_DIR, "brain_artifacts")
]

seen_paths = set()

for d, label in scan_dirs:
    if not os.path.exists(d):
        continue
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if os.path.isdir(p) or p in seen_paths or f.startswith('._') or f == '.DS_Store':
            continue
        seen_paths.add(p)
        stat = os.stat(p)
        ext = os.path.splitext(f)[1].lower()
        sha = sha256_file(p)
        dim = ""
        if ext == '.csv':
            try:
                df = pd.read_csv(p, nrows=1)
                with open(p, 'rb') as fp:
                    lines = sum(1 for _ in fp)
                dim = f"{lines - 1} rows x {len(df.columns)} cols"
            except Exception as e:
                dim = "csv read error"
        purpose, deps = get_purpose_and_deps(f, label)
        records.append({
            'filename': f,
            'actual_path': p,
            'location_category': label,
            'file_type': ext,
            'size_bytes': stat.st_size,
            'dimensions': dim,
            'last_modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'sha256_hash': sha,
            'purpose': purpose,
            'dependencies': deps
        })

df_provenance = pd.DataFrame(records)
df_provenance.to_csv(OUT_CSV, index=False)
print(f"Generated phase4_5_data_provenance.csv with {len(df_provenance)} entries.")
