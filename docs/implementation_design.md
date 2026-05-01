# Implementation Design

## Package Layout

```
src/adef/          # installable package (pythonpath = ["src"] in pyproject.toml)
tests/             # pytest test suite
examples/          # runnable demo scripts
docs/              # documentation
```

The `src/` layout prevents accidental imports from the project root during testing,
ensuring the installed package is always on the path.

## Exception Hierarchy

```
ADEFError (base)
├── IngestionError
├── ValidationError
├── TransformationError
├── QualityError
├── MetadataStoreError
├── LineageError
└── PipelineError
```

Each stage raises its own subclass, enabling callers to catch specific failures without
swallowing unrelated exceptions.

## Configuration Schema

```yaml
pipeline:
  name: <str>           # pipeline identifier

schema:
  required_columns: []  # list of column names that must be present
  column_types: {}      # column → "integer" | "float"
  allowed_values: {}    # column → [list of permitted string values]

transformations:        # ordered list of rule dicts
  - type: rename_column
    from: <src>
    to: <dst>
  - type: drop_column
    column: <name>
  - type: derive_column
    name: <new_col>
    columns: [<col1>, <col2>]
    separator: " "
  - type: normalize_column
    column: <name>
    operation: uppercase | lowercase | strip
  - type: cast_type
    column: <name>
    to: integer | float | string

quality:
  max_missing_pct: <float>      # fail if missing% exceeds this
  max_duplicate_pct: <float>    # fail if dup% exceeds this
  min_quality_score: <float>    # fail if score falls below this
```

## Data Flow

```
run_pipeline()
  ├── load_yaml(config_path)
  ├── initialize_store(db_path)           # create SQLite tables
  ├── ingest_csv(input_path)              # → (df, metadata)
  │     store_metadata(metadata, db)
  │     log_event("ingest", ...)
  │     record_lineage("ingestion", ...)
  ├── validate_schema(df, config)         # → validation_result
  │     store_validation(dataset_id, result, db)
  │     log_event("validate", ...)
  │     record_lineage("validation", ...)
  ├── apply_transformations(df, config)   # → (df_transformed, transform_log)
  │     log_event("transform", ...)
  │     record_lineage("transformation", ...)
  ├── run_quality_checks(df_transformed, config)  # → quality_result
  │     store_quality(dataset_id, result, db)
  │     log_event("quality_check", ...)
  │     record_lineage("quality_check", ...)
  ├── store_run(run_id, summary, db)
  ├── log_event("pipeline_complete", ...)
  └── return summary
```
