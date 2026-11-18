"""
Configuration settings and constants for SupeRR Selector Season 2 Dashboard.
Provides environment-agnostic relative paths and unified theme definitions.
"""
from pathlib import Path

# Project paths (Relative to repository root)
APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
DATA_DIR = ROOT_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"
ASSETS_DIR = ROOT_DIR / "assets"

# Canonical Filenames
FILE_TOP10_BATTERS = PROCESSED_DIR / "top10_batters.csv"
FILE_TOP10_BOWLERS = PROCESSED_DIR / "top10_bowlers.csv"
FILE_BATTING_RANKING = PROCESSED_DIR / "batting_ranking_full.csv"
FILE_BOWLING_RANKING = PROCESSED_DIR / "bowling_ranking_full.csv"
FILE_BATTING_FEATURES = PROCESSED_DIR / "batting_pressure_features.csv"
FILE_BOWLING_FEATURES = PROCESSED_DIR / "bowling_pressure_features.csv"
FILE_DELIVERIES_PRESSURE = PROCESSED_DIR / "deliveries_with_pressure.csv"
FILE_SENSITIVITY = PROCESSED_DIR / "phase4_sensitivity_results.csv"
FILE_RAW_BALLS = RAW_DIR / "ball_by_ball.csv"
FILE_RAW_MATCHES = RAW_DIR / "matches.csv"

# Verified Benchmark Figures (Phase 4.5.2 Ground Truth)
TOTAL_DELIVERIES_EXPECTED = 200999
PRESSURE_RECORDS_EXPECTED = 26735
PRESSURE_BATTER_BF_EXPECTED = 25518
PRESSURE_BOWLER_LEGAL_EXPECTED = 25358
FULL_DATASET_BATTER_BF_EXPECTED = 193284
MATCHES_SCHEDULED_EXPECTED = 883
MATCHES_PLAYED_EXPECTED = 867
COMPETITIONS_EXPECTED = 138
BATTER_QUALIFIED_COUNT = 153
BOWLER_QUALIFIED_COUNT = 133

# Operational Thresholds
PRESSURE_THRESHOLD = 45.0
BATTER_MIN_BALLS = 50
BOWLER_MIN_BALLS = 60
PAR_SCORE_1ST_INNINGS = 165.0

# Empirical Bayes Tournament Priors
BAT_PRIOR_MU = 136.07
BAT_PRIOR_N0 = 28.64
BOWL_PRIOR_MU = 8.33
BOWL_PRIOR_B0 = 33.82

# Theme Palette (Rajasthan Royals Elite Dark Sports-Analytics)
COLOR_NAVY_BG = "#0F172A"       # Deep Navy Background
COLOR_CARD_BG = "#1E293B"       # Slate Surface Card
COLOR_CARD_BORDER = "#334155"   # Card Border
COLOR_BATTING = "#E11D48"       # RR Pink / Crimson
COLOR_BATTING_LIGHT = "#FDA4AF" # Light Pink Accent
COLOR_BOWLING = "#0EA5E9"       # Electric Cyan
COLOR_BOWLING_LIGHT = "#7DD3FC" # Soft Cyan Accent
COLOR_CRITICAL = "#BE123C"      # Critical Pressure (P >= 70)
COLOR_HIGH = "#F59E0B"          # High Pressure (45 <= P < 70)
COLOR_MODERATE = "#38BDF8"      # Moderate Pressure (20 <= P < 45)
COLOR_LOW = "#64748B"           # Low Pressure (P < 20)
COLOR_TEXT_PRIMARY = "#F8FAFC"  # High-Contrast White
COLOR_TEXT_MUTED = "#94A3B8"    # Slate Secondary Text
COLOR_EMERALD = "#10B981"       # Success / Positive KPI
COLOR_AMBER = "#F59E0B"         # Warning / Alert

# Plotly Shared Layout Config
PLOTLY_DARK_LAYOUT = dict(
    paper_bgcolor=COLOR_CARD_BG,
    plot_bgcolor=COLOR_CARD_BG,
    font=dict(family="sans-serif", color=COLOR_TEXT_PRIMARY, size=11),
    title=dict(font=dict(color=COLOR_TEXT_PRIMARY, size=14, family="sans-serif")),
    legend=dict(font=dict(color=COLOR_TEXT_PRIMARY, size=10), bgcolor="rgba(15, 23, 42, 0.6)"),
    margin=dict(l=40, r=40, t=50, b=40),
    xaxis=dict(gridcolor="#334155", zerolinecolor="#475569"),
    yaxis=dict(gridcolor="#334155", zerolinecolor="#475569")
)
