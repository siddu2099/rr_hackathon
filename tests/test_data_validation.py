"""
Unit tests for data validation module.
Verifies schemas, benchmark numbers, and mathematical invariants.
"""
import pytest
import pandas as pd

from app.config import (
    TOTAL_DELIVERIES_EXPECTED,
    PRESSURE_RECORDS_EXPECTED,
    PRESSURE_BATTER_BF_EXPECTED,
    PRESSURE_BOWLER_LEGAL_EXPECTED,
    FILE_TOP10_BATTERS,
    FILE_TOP10_BOWLERS,
    FILE_DELIVERIES_PRESSURE
)
from app.data_loader import (
    load_top10_batters,
    load_top10_bowlers,
    load_deliveries_pressure
)
from app.data_validation import (
    validate_source_files,
    validate_ranking_integrity,
    validate_numerical_integrity
)


def test_source_files_exist():
    """Verify that all required canonical CSV files exist in the repository."""
    file_status = validate_source_files()
    for name, exists in file_status.items():
        assert exists, f"Required file '{name}' is missing!"


def test_top10_rankings_integrity():
    """Verify integrity of canonical Top 10 Batters and Bowlers."""
    df_bat = load_top10_batters()
    df_bowl = load_top10_bowlers()
    
    results = validate_ranking_integrity(df_bat, df_bowl)
    assert results['batting_count_valid'], "Top 10 Batters must have exactly 10 rows"
    assert results['batting_ranks_monotonic'], "Batting ranks must be 1 to 10"
    assert results['batting_nulls_valid'], "Batting Top 10 has null names or BPRI scores"
    assert results['bowling_count_valid'], "Top 10 Bowlers must have exactly 10 rows"
    assert results['bowling_ranks_monotonic'], "Bowling ranks must be 1 to 10"
    assert results['bowling_nulls_valid'], "Bowling Top 10 has null names or BPRI scores"
    assert results['bowling_delta_sign_convention_valid'], "Bowling Delta Econ must follow positive suppression convention"
    assert results['overall_ranking_integrity'], "Ranking integrity checks failed"


def test_numerical_benchmarks():
    """Verify that delivery counts match verified Phase 4.5.2 ground truth."""
    df_deliv = load_deliveries_pressure(
        columns=['is_pressure_delivery', 'is_batter_ball', 'is_legal']
    )
    
    results = validate_numerical_integrity(df_deliv)
    assert results['total_deliveries_match'], f"Total deliveries {results['total_deliveries']} != {TOTAL_DELIVERIES_EXPECTED}"
    assert results['pressure_records_match'], f"Pressure records {results['pressure_records']} != {PRESSURE_RECORDS_EXPECTED}"
    assert results['pressure_batter_bf_match'], f"Pressure batter balls faced {results['pressure_batter_bf']} != {PRESSURE_BATTER_BF_EXPECTED}"
    assert results['pressure_bowler_legal_match'], f"Pressure bowler legal balls {results['pressure_bowler_legal']} != {PRESSURE_BOWLER_LEGAL_EXPECTED}"
    assert results['no_25876_typo'], "CRITICAL: 25,876 typo detected in pressure balls faced!"
    assert results['all_numerical_checks_passed'], "Numerical benchmark checks failed"
