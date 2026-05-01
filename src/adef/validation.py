import pandas as pd


def validate_schema(df: pd.DataFrame, config: dict) -> dict:
    schema_cfg = config.get("schema", {})
    checks: list[dict] = []
    passed_count = 0

    # Required columns
    required = schema_cfg.get("required_columns", [])
    missing_cols = [c for c in required if c not in df.columns]
    col_passed = len(missing_cols) == 0
    checks.append({
        "check": "required_columns",
        "passed": col_passed,
        "detail": "All required columns present" if col_passed
                  else f"Missing columns: {missing_cols}",
    })
    if col_passed:
        passed_count += 1

    # Column type validation
    for col, expected_type in schema_cfg.get("column_types", {}).items():
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if expected_type == "integer":
            numeric = pd.to_numeric(series, errors="coerce")
            type_ok = bool(numeric.notna().all() and (numeric == numeric.round()).all())
        elif expected_type == "float":
            type_ok = bool(pd.to_numeric(series, errors="coerce").notna().all())
        else:
            type_ok = True
        checks.append({
            "check": f"column_type_{col}",
            "passed": type_ok,
            "detail": f"'{col}' is valid {expected_type}" if type_ok
                      else f"'{col}' contains invalid {expected_type} values",
        })
        if type_ok:
            passed_count += 1

    # Allowed values
    for col, allowed in schema_cfg.get("allowed_values", {}).items():
        if col not in df.columns:
            continue
        invalid = df[col].dropna()[~df[col].dropna().isin(allowed)]
        av_passed = len(invalid) == 0
        checks.append({
            "check": f"allowed_values_{col}",
            "passed": av_passed,
            "detail": f"'{col}' values are valid" if av_passed
                      else f"'{col}' has {len(invalid)} invalid values: {invalid.unique().tolist()[:3]}",
        })
        if av_passed:
            passed_count += 1

    total = len(checks)
    score = round(passed_count / total * 100, 2) if total > 0 else 100.0

    return {
        "passed": all(c["passed"] for c in checks),
        "passed_count": passed_count,
        "total_checks": total,
        "score": score,
        "checks": checks,
    }
