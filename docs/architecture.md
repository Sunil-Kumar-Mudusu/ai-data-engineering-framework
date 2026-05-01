# Architecture

## Pipeline Stages

```
CSV File ──► Ingestion ──► Validation ──► Transformation ──► Quality Check
                │               │                │                 │
                ▼               ▼                ▼                 ▼
           Metadata DB    Validation DB    (in-memory)       Quality DB
                │               │                │                 │
                └───────────────┴────────────────┴─────────────────┘
                                        │
                              Lineage JSONL + Audit JSONL
```

## Modules

**`ingestion`** — reads a CSV file, computes SHA-256 checksum (first 16 hex chars), assigns a
UUID4 dataset ID, and returns a `(DataFrame, metadata)` tuple. The metadata dict carries
`source_name`, `row_count`, `column_count`, `checksum`, and `ingestion_timestamp`.

**`validation`** — checks required columns, numeric/integer type conformance, and allowed-value
sets. Returns a dict with `passed`, `score` (0–100), `total_checks`, and a `checks` list with
per-check pass/fail detail.

**`transformation`** — applies an ordered list of rules from the config: `rename_column`,
`drop_column`, `derive_column` (string concatenation), `normalize_column` (upper/lower/strip),
and `cast_type`. Returns a new DataFrame and a transformation log.

**`quality_engine`** — computes `missing_pct` and `duplicate_count`, then scores as
`completeness * 0.6 + uniqueness * 0.4` where completeness = `100 - missing_pct` and
uniqueness = `100 - dup_pct`. Returns `passed` based on config thresholds.

**`lineage_tracker`** — appends one JSONL record per stage with `dataset_id`, `step`,
`inputs`, `outputs`, `metadata`, and `timestamp`.

**`audit_logger`** — appends one JSONL record per event with `action`, `dataset_id`, `status`,
`detail`, `actor`, and `timestamp`.

**`metadata_store`** — SQLite-backed store with four tables: `pipeline_runs`,
`dataset_metadata`, `validation_results`, `quality_results`.

**`pipeline_runner`** — top-level orchestrator that chains all four stages and returns a
`summary` dict.

## Design Decisions

- **JSONL for lineage and audit**: append-only, human-readable, no schema migration.
- **SQLite for metadata**: queryable via `query_runs()` / `query_datasets()` without an
  external database dependency.
- **Config-driven transformations**: rules declared in YAML, no code changes required for
  new transformation sequences.
- **Immutable DataFrames**: `transformation.py` works on a `df.copy()` so the original is
  never mutated.
