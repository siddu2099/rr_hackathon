"""
Data loader module for SupeRR Selector Season 2 Dashboard.
Provides cached, optimized access to canonical processed datasets.
"""
from pathlib import Path
from typing import Optional, List
import pandas as pd
import streamlit as st

from app.config import (
    FILE_TOP10_BATTERS,
    FILE_TOP10_BOWLERS,
    FILE_BATTING_RANKING,
    FILE_BOWLING_RANKING,
    FILE_BATTING_FEATURES,
    FILE_BOWLING_FEATURES,
    FILE_DELIVERIES_PRESSURE,
    FILE_SENSITIVITY,
    FILE_RAW_MATCHES,
    FILE_RAW_BALLS
)


@st.cache_data(show_spinner=False)
def load_top10_batters() -> pd.DataFrame:
    """Load canonical Top 10 Batters leaderboard."""
    if not FILE_TOP10_BATTERS.exists():
        raise FileNotFoundError(f"Top 10 Batters file missing: {FILE_TOP10_BATTERS}")
    df = pd.read_csv(FILE_TOP10_BATTERS)
    # Ensure rank is int
    if 'rank' in df.columns:
        df['rank'] = df['rank'].astype(int)
    return df


@st.cache_data(show_spinner=False)
def load_top10_bowlers() -> pd.DataFrame:
    """Load canonical Top 10 Bowlers leaderboard."""
    if not FILE_TOP10_BOWLERS.exists():
        raise FileNotFoundError(f"Top 10 Bowlers file missing: {FILE_TOP10_BOWLERS}")
    df = pd.read_csv(FILE_TOP10_BOWLERS)
    if 'rank' in df.columns:
        df['rank'] = df['rank'].astype(int)
    return df


@st.cache_data(show_spinner=False)
def load_batting_rankings() -> pd.DataFrame:
    """Load complete qualified batting rankings (153 batters)."""
    if not FILE_BATTING_RANKING.exists():
        raise FileNotFoundError(f"Batting ranking file missing: {FILE_BATTING_RANKING}")
    df = pd.read_csv(FILE_BATTING_RANKING)
    if 'rank' in df.columns:
        df['rank'] = df['rank'].astype(int)
    return df


@st.cache_data(show_spinner=False)
def load_bowling_rankings() -> pd.DataFrame:
    """Load complete qualified bowling rankings (133 bowlers)."""
    if not FILE_BOWLING_RANKING.exists():
        raise FileNotFoundError(f"Bowling ranking file missing: {FILE_BOWLING_RANKING}")
    df = pd.read_csv(FILE_BOWLING_RANKING)
    if 'rank' in df.columns:
        df['rank'] = df['rank'].astype(int)
    return df


@st.cache_data(show_spinner=False)
def load_batting_features() -> pd.DataFrame:
    """Load player-level batting pressure aggregations (all 724 batters)."""
    if not FILE_BATTING_FEATURES.exists():
        raise FileNotFoundError(f"Batting features file missing: {FILE_BATTING_FEATURES}")
    return pd.read_csv(FILE_BATTING_FEATURES)


@st.cache_data(show_spinner=False)
def load_bowling_features() -> pd.DataFrame:
    """Load player-level bowling pressure aggregations (all 604 bowlers)."""
    if not FILE_BOWLING_FEATURES.exists():
        raise FileNotFoundError(f"Bowling features file missing: {FILE_BOWLING_FEATURES}")
    return pd.read_csv(FILE_BOWLING_FEATURES)


@st.cache_data(show_spinner=True)
def load_deliveries_pressure(
    columns: Optional[List[str]] = None,
    pressure_only: bool = False
) -> pd.DataFrame:
    """
    Load delivery-level dataset with calculated pressure.
    Uses memory-efficient dtypes to ensure fast performance.
    """
    if not FILE_DELIVERIES_PRESSURE.exists():
        raise FileNotFoundError(f"Deliveries with pressure file missing: {FILE_DELIVERIES_PRESSURE}")
    
    # Specify downcasted types for key columns
    dtype_map = {
        'match_id': 'int32',
        'innings': 'int8',
        'overid': 'int8',
        'over_ball_num': 'int8',
        'comp_category': 'category',
        'pressure_tier': 'category',
        'is_pressure_delivery': 'bool',
        'is_legal': 'bool',
        'is_batter_ball': 'bool',
        'is_wicket': 'bool',
        'is_bowler_wicket': 'bool',
        'is_four': 'bool',
        'is_six': 'bool',
        'runs': 'int8',
        'bowler_runs_conceded': 'int8',
        'pressure_score': 'float32'
    }
    
    # If specific columns requested, subset dtypes
    if columns:
        read_dtypes = {k: v for k, v in dtype_map.items() if k in columns}
        df = pd.read_csv(FILE_DELIVERIES_PRESSURE, usecols=columns, dtype=read_dtypes, low_memory=False)
    else:
        df = pd.read_csv(FILE_DELIVERIES_PRESSURE, dtype=dtype_map, low_memory=False)
        
    if pressure_only:
        df = df[df['is_pressure_delivery']].copy()
        
    return df


@st.cache_data(show_spinner=False)
def load_sensitivity_results() -> pd.DataFrame:
    """Load threshold, weight, and volume sensitivity testing results."""
    if not FILE_SENSITIVITY.exists():
        return pd.DataFrame()
    return pd.read_csv(FILE_SENSITIVITY)


@st.cache_data(show_spinner=False)
def load_matches_metadata() -> pd.DataFrame:
    """Load raw match schedule metadata if available."""
    if not FILE_RAW_MATCHES.exists():
        return pd.DataFrame()
    return pd.read_csv(FILE_RAW_MATCHES)
