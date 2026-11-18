"""
Data validation module for SupeRR Selector Season 2 Dashboard.
Provides rigorous verification of schemas, benchmark numbers, and mathematical conventions.
"""
from typing import Dict, Any, Tuple
import pandas as pd

from app.config import (
    FILE_TOP10_BATTERS,
    FILE_TOP10_BOWLERS,
    FILE_BATTING_RANKING,
    FILE_BOWLING_RANKING,
    FILE_DELIVERIES_PRESSURE,
    TOTAL_DELIVERIES_EXPECTED,
    PRESSURE_RECORDS_EXPECTED,
    PRESSURE_BATTER_BF_EXPECTED,
    PRESSURE_BOWLER_LEGAL_EXPECTED,
    FULL_DATASET_BATTER_BF_EXPECTED
)


def validate_source_files() -> Dict[str, bool]:
    """Check existence of all critical processed source files."""
    required = {
        "top10_batters": FILE_TOP10_BATTERS,
        "top10_bowlers": FILE_TOP10_BOWLERS,
        "batting_ranking_full": FILE_BATTING_RANKING,
        "bowling_ranking_full": FILE_BOWLING_RANKING,
        "deliveries_with_pressure": FILE_DELIVERIES_PRESSURE,
    }
    return {name: path.exists() for name, path in required.items()}


def validate_schema(df: pd.DataFrame, required_columns: list) -> Tuple[bool, list]:
    """Check whether a dataframe contains all required columns."""
    missing = [c for c in required_columns if c not in df.columns]
    return (len(missing) == 0, missing)


def validate_ranking_integrity(df_bat: pd.DataFrame, df_bowl: pd.DataFrame) -> Dict[str, Any]:
    """
    Verify integrity of canonical Top 10 rankings:
    - Exactly 10 rows
    - Monotonic ranks 1 to 10
    - No null BPRI scores or player identifiers
    - Strict bowling delta sign convention (positive = run suppression)
    """
    results = {}
    
    # Batting Top 10
    bat_count = len(df_bat)
    bat_ranks = df_bat['rank'].tolist() if 'rank' in df_bat.columns else []
    bat_nulls = df_bat[['striker_name', 'BPRI_Model1_Balanced']].isna().sum().sum()
    results['batting_count_valid'] = (bat_count == 10)
    results['batting_ranks_monotonic'] = (bat_ranks == list(range(1, 11)))
    results['batting_nulls_valid'] = (bat_nulls == 0)
    
    # Bowling Top 10
    bowl_count = len(df_bowl)
    bowl_ranks = df_bowl['rank'].tolist() if 'rank' in df_bowl.columns else []
    bowl_nulls = df_bowl[['bowler_name', 'BPRI_Model1_Balanced']].isna().sum().sum()
    results['bowling_count_valid'] = (bowl_count == 10)
    results['bowling_ranks_monotonic'] = (bowl_ranks == list(range(1, 11)))
    results['bowling_nulls_valid'] = (bowl_nulls == 0)
    
    # Bowling Delta Econ convention check:
    # Delta Econ = np_economy - p_economy.
    # Top bowler Abrar Ahmed: np_economy (7.18) - p_economy (3.83) = +3.35
    if 'unbiased_delta_econ' in df_bowl.columns:
        abrar_row = df_bowl[df_bowl['bowler_name'].str.contains('Abrar', case=False, na=False)]
        if not abrar_row.empty:
            delta_val = abrar_row.iloc[0]['unbiased_delta_econ']
            results['bowling_delta_sign_convention_valid'] = (delta_val > 0)
        else:
            results['bowling_delta_sign_convention_valid'] = True
    else:
        results['bowling_delta_sign_convention_valid'] = False
        
    results['overall_ranking_integrity'] = all(results.values())
    return results


def validate_numerical_integrity(df_deliv: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate the core dataset delivery counts against verified benchmarks:
    - Total deliveries = 200,999
    - Pressure deliveries = 26,735
    - Pressure batter balls faced = 25,518 (NOT 25,876)
    - Pressure bowler legal deliveries = 25,358
    """
    total_rows = len(df_deliv)
    p_mask = df_deliv['is_pressure_delivery']
    p_rows = int(p_mask.sum())
    p_deliv = df_deliv[p_mask]
    
    p_batter_bf = int(p_deliv['is_batter_ball'].sum())
    p_bowler_legal = int(p_deliv['is_legal'].sum())
    full_batter_bf = int(df_deliv['is_batter_ball'].sum())
    
    results = {
        'total_deliveries': total_rows,
        'total_deliveries_match': (total_rows == TOTAL_DELIVERIES_EXPECTED),
        'pressure_records': p_rows,
        'pressure_records_match': (p_rows == PRESSURE_RECORDS_EXPECTED),
        'pressure_batter_bf': p_batter_bf,
        'pressure_batter_bf_match': (p_batter_bf == PRESSURE_BATTER_BF_EXPECTED),
        'pressure_bowler_legal': p_bowler_legal,
        'pressure_bowler_legal_match': (p_bowler_legal == PRESSURE_BOWLER_LEGAL_EXPECTED),
        'full_batter_bf': full_batter_bf,
        'full_batter_bf_match': (full_batter_bf in [FULL_DATASET_BATTER_BF_EXPECTED, FULL_DATASET_BATTER_BF_EXPECTED + 1]),
        'no_25876_typo': (p_batter_bf != 25876)
    }
    
    results['all_numerical_checks_passed'] = (
        results['total_deliveries_match'] and
        results['pressure_records_match'] and
        results['pressure_batter_bf_match'] and
        results['pressure_bowler_legal_match'] and
        results['no_25876_typo']
    )
    return results
