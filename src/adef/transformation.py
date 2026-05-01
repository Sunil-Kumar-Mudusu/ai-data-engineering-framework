import pandas as pd


def apply_transformations(df: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, list[dict]]:
    df = df.copy()
    log: list[dict] = []

    for rule in config.get("transformations", []):
        rule_type = rule.get("type")

        if rule_type == "rename_column":
            src, dst = rule.get("from"), rule.get("to")
            if src in df.columns:
                df = df.rename(columns={src: dst})
                log.append({"type": rule_type, "from": src, "to": dst, "status": "applied"})
            else:
                log.append({"type": rule_type, "from": src, "status": "skipped", "reason": "column not found"})

        elif rule_type == "drop_column":
            col = rule.get("column")
            if col in df.columns:
                df = df.drop(columns=[col])
                log.append({"type": rule_type, "column": col, "status": "applied"})
            else:
                log.append({"type": rule_type, "column": col, "status": "skipped", "reason": "column not found"})

        elif rule_type == "derive_column":
            name = rule.get("name")
            cols = rule.get("columns", [])
            separator = rule.get("separator", " ")
            available = [c for c in cols if c in df.columns]
            if available:
                df[name] = df[available].fillna("").astype(str).apply(
                    lambda row: separator.join(v for v in row if v), axis=1
                )
                log.append({"type": rule_type, "name": name, "columns": available, "status": "applied"})
            else:
                log.append({"type": rule_type, "name": name, "status": "skipped", "reason": "source columns not found"})

        elif rule_type == "normalize_column":
            col = rule.get("column")
            operation = rule.get("operation", "lowercase")
            if col in df.columns:
                ops = {"uppercase": str.upper, "lowercase": str.lower, "strip": str.strip}
                if operation in ops:
                    df[col] = df[col].str.upper() if operation == "uppercase" \
                        else df[col].str.lower() if operation == "lowercase" \
                        else df[col].str.strip()
                log.append({"type": rule_type, "column": col, "operation": operation, "status": "applied"})
            else:
                log.append({"type": rule_type, "column": col, "status": "skipped", "reason": "column not found"})

        elif rule_type == "cast_type":
            col = rule.get("column")
            target = rule.get("to") or rule.get("target_type")
            if col in df.columns:
                try:
                    if target == "integer":
                        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                    elif target == "float":
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                    elif target == "string":
                        df[col] = df[col].astype(str)
                    log.append({"type": rule_type, "column": col, "target_type": target, "status": "applied"})
                except Exception as exc:
                    log.append({"type": rule_type, "column": col, "status": "failed", "reason": str(exc)})

        else:
            log.append({"type": rule_type, "status": "unknown", "reason": "unsupported rule type"})

    return df, log
