import pandas as pd
import pytest

from adef.transformation import apply_transformations


def _cfg(rules):
    return {"transformations": rules}


@pytest.fixture()
def base_df():
    return pd.DataFrame({
        "first_name": ["Alice", "Bob"],
        "last_name": ["Smith", "Jones"],
        "salary": [50000.0, 60000.0],
        "status": ["active", "inactive"],
    })


def test_returns_df_and_log(base_df):
    df_out, log = apply_transformations(base_df, _cfg([]))
    assert isinstance(df_out, pd.DataFrame)
    assert isinstance(log, list)


def test_rename_column(base_df):
    rules = [{"type": "rename_column", "from": "first_name", "to": "given_name"}]
    df_out, _ = apply_transformations(base_df, _cfg(rules))
    assert "given_name" in df_out.columns
    assert "first_name" not in df_out.columns


def test_drop_column(base_df):
    rules = [{"type": "drop_column", "column": "salary"}]
    df_out, _ = apply_transformations(base_df, _cfg(rules))
    assert "salary" not in df_out.columns


def test_derive_column(base_df):
    rules = [{"type": "derive_column", "name": "full_name",
               "columns": ["first_name", "last_name"], "separator": " "}]
    df_out, _ = apply_transformations(base_df, _cfg(rules))
    assert "full_name" in df_out.columns
    assert df_out["full_name"].iloc[0] == "Alice Smith"


def test_normalize_uppercase(base_df):
    rules = [{"type": "normalize_column", "column": "status", "operation": "uppercase"}]
    df_out, _ = apply_transformations(base_df, _cfg(rules))
    assert df_out["status"].iloc[0] == "ACTIVE"


def test_normalize_lowercase(base_df):
    rules = [{"type": "normalize_column", "column": "status", "operation": "lowercase"}]
    df_out, _ = apply_transformations(base_df, _cfg(rules))
    assert df_out["status"].iloc[0] == "active"


def test_normalize_strip():
    df = pd.DataFrame({"name": ["  Alice  ", " Bob "]})
    rules = [{"type": "normalize_column", "column": "name", "operation": "strip"}]
    df_out, _ = apply_transformations(df, _cfg(rules))
    assert df_out["name"].iloc[0] == "Alice"


def test_cast_type_integer():
    df = pd.DataFrame({"val": ["1", "2", "3"]})
    rules = [{"type": "cast_type", "column": "val", "to": "integer"}]
    df_out, _ = apply_transformations(df, _cfg(rules))
    assert str(df_out["val"].dtype).lower() in ("int64", "int32", "int64", "uint64", "int8", "int16") or \
           "int" in str(df_out["val"].dtype).lower()


def test_log_records_applied_status(base_df):
    rules = [{"type": "rename_column", "from": "first_name", "to": "given_name"}]
    _, log = apply_transformations(base_df, _cfg(rules))
    assert log[0]["status"] == "applied"


def test_unknown_rule_skipped(base_df):
    rules = [{"type": "nonexistent_rule", "column": "x"}]
    df_out, log = apply_transformations(base_df, _cfg(rules))
    assert log[0]["status"] == "unknown"


def test_original_df_not_mutated(base_df):
    original_cols = list(base_df.columns)
    rules = [{"type": "rename_column", "from": "first_name", "to": "given_name"}]
    apply_transformations(base_df, _cfg(rules))
    assert list(base_df.columns) == original_cols
