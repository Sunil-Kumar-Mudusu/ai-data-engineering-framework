import pandas as pd


def run_quality_checks(df: pd.DataFrame, config: dict) -> dict:
    quality_cfg = config.get("quality", {})
    max_missing_pct = quality_cfg.get("max_missing_pct", 10.0)
    max_duplicate_pct = quality_cfg.get("max_duplicate_pct", 5.0)

    row_count = len(df)
    total_cells = row_count * len(df.columns)

    missing_cells = int(df.isnull().sum().sum())
    missing_pct = round(missing_cells / total_cells * 100, 2) if total_cells > 0 else 0.0

    dup_count = int(df.duplicated().sum())
    dup_pct = round(dup_count / row_count * 100, 2) if row_count > 0 else 0.0

    col_nulls = {col: int(df[col].isnull().sum()) for col in df.columns if df[col].isnull().any()}

    completeness = round(max(0.0, 100.0 - missing_pct), 2)
    uniqueness = round(max(0.0, 100.0 - dup_pct), 2)
    quality_score = round(completeness * 0.6 + uniqueness * 0.4, 2)

    checks = [
        {
            "check": "missing_values",
            "passed": missing_pct <= max_missing_pct,
            "value": missing_pct,
            "threshold": max_missing_pct,
            "detail": f"Missing: {missing_pct}% (limit {max_missing_pct}%)",
        },
        {
            "check": "duplicate_rows",
            "passed": dup_pct <= max_duplicate_pct,
            "value": dup_pct,
            "threshold": max_duplicate_pct,
            "detail": f"Duplicates: {dup_count} rows / {dup_pct}% (limit {max_duplicate_pct}%)",
        },
    ]

    return {
        "passed": all(c["passed"] for c in checks),
        "quality_score": quality_score,
        "completeness": completeness,
        "uniqueness": uniqueness,
        "missing_cells": missing_cells,
        "missing_pct": missing_pct,
        "duplicate_count": dup_count,
        "duplicate_pct": dup_pct,
        "column_nulls": col_nulls,
        "checks": checks,
    }
