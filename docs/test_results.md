# Test Results

Verified on: 2026-05-12
Platform: Windows 11, Python 3.14
Command: `pytest -q`

## pytest output

```
75 passed in 1.13s
```

## Pipeline demo output

Command: `python examples/sample_pipeline.py`

```
============================================================
  AI Data Engineering Framework — Pipeline Run
============================================================

  Pipeline   : workforce_data_pipeline
  Run ID     : d95d49c9-6b80-4f91-810b-b4608b0cf0c4
  Dataset ID : fba644e6-989c-4c28-a509-e12544eb99f8
  Source     : sample_input.csv

[1] Ingestion
    rows       : 18
    columns    : 8
    checksum   : dd0a77147425c43e...

[2] Schema Validation
    passed     : True
    score      : 100.0/100
    checks run : 5

[3] Transformation
    rules applied  : 4
    output columns : 9

[4] Data Quality
    passed     : True
    score      : 99.63/100
    missing    : 0.62%
    duplicates : 0 rows

============================================================
  VERIFICATION SUMMARY
============================================================
  Pipeline      : workforce_data_pipeline
  Status        : SUCCESS
  Validation    : PASSED (100.0/100)
  Quality Score : 99.63/100 (PASSED)
  Lineage Steps : 4
  Audit Events  : 5
============================================================
```

## Notes

- The 0.62% missing rate is from Eve Jones (row 5) whose `annual_salary` is blank.
- All 5 schema checks passed: 6 required columns present, `record_id` is integer,
  `annual_salary` is float, `employment_status` and `department` values are in allowed sets.
- 4 transformation rules applied: rename `first_name` → `given_name`, rename `last_name`
  → `family_name`, derive `full_name`, normalize `employment_status` to uppercase.
- Run ID and Dataset ID are UUID4-generated and will differ between runs.
