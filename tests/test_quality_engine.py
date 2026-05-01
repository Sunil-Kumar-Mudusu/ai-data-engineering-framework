import pandas as pd
import pytest

from adef.quality_engine import run_quality_checks


def _cfg(max_missing=10.0, max_dup=5.0, min_score=75.0):
    return {
        "quality": {
            "max_missing_pct": max_missing,
            "max_duplicate_pct": max_dup,
            "min_quality_score": min_score,
        }
    }


@pytest.fixture()
def clean_df():
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["A", "B", "C", "D", "E"],
        "val": [10.0, 20.0, 30.0, 40.0, 50.0],
    })


def test_returns_dict(clean_df):
    result = run_quality_checks(clean_df, _cfg())
    assert isinstance(result, dict)


def test_clean_data_passes(clean_df):
    result = run_quality_checks(clean_df, _cfg())
    assert result["passed"] is True


def test_quality_score_present(clean_df):
    result = run_quality_checks(clean_df, _cfg())
    assert "quality_score" in result
    assert 0 <= result["quality_score"] <= 100


def test_missing_pct_zero_for_clean(clean_df):
    result = run_quality_checks(clean_df, _cfg())
    assert result["missing_pct"] == 0.0


def test_duplicate_count_zero_for_clean(clean_df):
    result = run_quality_checks(clean_df, _cfg())
    assert result["duplicate_count"] == 0


def test_detects_missing_values():
    df = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "val": [10.0, None, None, 40.0, 50.0],
    })
    result = run_quality_checks(df, _cfg(max_missing=5.0))
    assert result["missing_pct"] > 0
    assert result["passed"] is False


def test_detects_duplicates():
    df = pd.DataFrame({
        "id": [1, 1, 2, 3, 4],
        "val": [10.0, 10.0, 20.0, 30.0, 40.0],
    })
    result = run_quality_checks(df, _cfg(max_dup=0.0))
    assert result["duplicate_count"] >= 1
    assert result["passed"] is False


def test_high_missing_fails():
    df = pd.DataFrame({"a": [None] * 9 + [1.0]})
    result = run_quality_checks(df, _cfg(max_missing=10.0, min_score=75.0))
    assert result["passed"] is False


def test_passes_false_when_score_below_min():
    df = pd.DataFrame({"a": [None] * 8 + [1.0, 2.0]})
    result = run_quality_checks(df, _cfg(min_score=95.0))
    assert result["passed"] is False


def test_column_nulls_in_result(clean_df):
    result = run_quality_checks(clean_df, _cfg())
    assert "column_nulls" in result
    assert isinstance(result["column_nulls"], dict)


def test_checks_list_present(clean_df):
    result = run_quality_checks(clean_df, _cfg())
    assert "checks" in result
    assert isinstance(result["checks"], list)
