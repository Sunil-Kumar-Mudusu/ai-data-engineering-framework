import pandas as pd
import pytest

from adef.validation import validate_schema


def _config(required=None, types=None, allowed=None):
    return {
        "schema": {
            "required_columns": required or [],
            "column_types": types or {},
            "allowed_values": allowed or {},
        }
    }


@pytest.fixture()
def base_df():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Carol"],
        "status": ["active", "inactive", "active"],
    })


def test_returns_dict(base_df):
    result = validate_schema(base_df, _config())
    assert isinstance(result, dict)


def test_passes_with_no_rules(base_df):
    result = validate_schema(base_df, _config())
    assert result["passed"] is True


def test_score_100_with_no_rules(base_df):
    result = validate_schema(base_df, _config())
    assert result["score"] == 100


def test_required_column_present(base_df):
    result = validate_schema(base_df, _config(required=["id", "name"]))
    assert result["passed"] is True


def test_required_column_missing(base_df):
    result = validate_schema(base_df, _config(required=["id", "missing_col"]))
    assert result["passed"] is False
    assert result["score"] < 100


def test_type_check_integer_passes(base_df):
    result = validate_schema(base_df, _config(types={"id": "integer"}))
    assert result["passed"] is True


def test_type_check_integer_fails():
    df = pd.DataFrame({"id": ["a", "b", "c"]})
    result = validate_schema(df, _config(types={"id": "integer"}))
    assert result["passed"] is False


def test_allowed_values_passes(base_df):
    result = validate_schema(
        base_df, _config(allowed={"status": ["active", "inactive"]})
    )
    assert result["passed"] is True


def test_allowed_values_fails():
    df = pd.DataFrame({"status": ["active", "unknown"]})
    result = validate_schema(
        df, _config(allowed={"status": ["active", "inactive"]})
    )
    assert result["passed"] is False


def test_total_checks_counted(base_df):
    result = validate_schema(
        base_df,
        _config(required=["id"], types={"id": "integer"}, allowed={"status": ["active", "inactive"]}),
    )
    assert result["total_checks"] >= 3


def test_issues_list_present(base_df):
    result = validate_schema(base_df, _config(required=["nonexistent"]))
    assert "checks" in result
    assert len(result["checks"]) > 0
    assert any(not c["passed"] for c in result["checks"])
