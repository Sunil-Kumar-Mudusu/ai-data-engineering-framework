# AI Data Engineering Framework

A production-ready Python implementation of the AI Data Engineering Framework described in:

> Mudusu, S. K. (2025). AI Data Engineering Framework.
> *JRTCSE — Journal of Research Trends in Computer Science and Engineering*, Vol. 13, No. 1.
> https://jrtcse.com/index.php/home/article/view/JRTCSE.2025.13.1.12

The framework was originally conceptualized in early 2025 and formalized as a GitHub reference
implementation on May 12, 2026.

---

## Overview

Modern data engineering pipelines must handle heterogeneous sources, enforce quality contracts,
and provide full lineage traceability. This framework operationalizes those requirements through
a modular, config-driven pipeline with four stages:

| Stage | Module | Purpose |
|---|---|---|
| Ingestion | `ingestion` | Load CSV, compute SHA-256 checksum, assign UUID dataset ID |
| Schema Validation | `validation` | Enforce required columns, types, and allowed values |
| Transformation | `transformation` | Rename, drop, derive, normalize, and cast columns |
| Data Quality | `quality_engine` | Score completeness and uniqueness; detect duplicates |

Supporting services — audit logging, lineage tracking, and SQLite metadata storage — run
transparently across all stages.

---

## Project Structure

```
ai-data-engineering-framework/
├── src/adef/
│   ├── __init__.py
│   ├── exceptions.py        # Domain-specific exception hierarchy
│   ├── config.py            # YAML config loader
│   ├── ingestion.py         # CSV ingestion + metadata extraction
│   ├── validation.py        # Schema validation engine
│   ├── transformation.py    # Config-driven data transformation
│   ├── quality_engine.py    # Quality scoring and checks
│   ├── lineage_tracker.py   # JSONL lineage recorder
│   ├── audit_logger.py      # JSONL immutable audit log
│   ├── metadata_store.py    # SQLite persistence layer
│   └── pipeline_runner.py   # Pipeline orchestrator
├── tests/                   # 75 pytest tests
├── examples/
│   ├── sample_pipeline.py   # End-to-end demonstration
│   ├── pipeline_config.yaml # Workforce pipeline configuration
│   └── sample_input.csv     # 18-row employee dataset
├── docs/
│   ├── architecture.md
│   ├── article_mapping.md
│   ├── implementation_design.md
│   ├── verification_checklist.md
│   └── test_results.md
├── .github/workflows/ci.yml
├── Dockerfile
├── pyproject.toml
└── requirements.txt
```

---

## Quick Start

```bash
git clone https://github.com/Sunil-Kumar-Mudusu/ai-data-engineering-framework
cd ai-data-engineering-framework
pip install -e ".[dev]"
pytest -q
python examples/sample_pipeline.py
```

---

## Pipeline Configuration

```yaml
pipeline:
  name: workforce_data_pipeline

schema:
  required_columns: [record_id, first_name, last_name, department, email, employment_status]
  column_types:
    record_id: integer
    annual_salary: float
  allowed_values:
    employment_status: [active, inactive]

transformations:
  - type: rename_column
    from: first_name
    to: given_name
  - type: derive_column
    name: full_name
    columns: [given_name, family_name]
    separator: " "
  - type: normalize_column
    column: employment_status
    operation: uppercase

quality:
  max_missing_pct: 10.0
  max_duplicate_pct: 5.0
  min_quality_score: 75.0
```

### Supported transformation types

| Type | Parameters | Effect |
|---|---|---|
| `rename_column` | `from`, `to` | Rename a column |
| `drop_column` | `column` | Remove a column |
| `derive_column` | `name`, `columns`, `separator` | Concatenate columns |
| `normalize_column` | `column`, `operation` | `uppercase` / `lowercase` / `strip` |
| `cast_type` | `column`, `to` | Cast to `integer`, `float`, or `string` |

---

## API

```python
from adef.pipeline_runner import run_pipeline

summary = run_pipeline(
    config_path="examples/pipeline_config.yaml",
    input_path="examples/sample_input.csv",
    db_path="run.db",
    lineage_path="lineage.jsonl",
    log_path="audit.jsonl",
)
print(summary["stages"]["quality"]["score"])   # e.g. 99.63
```

---

## Verified Results

```
75 passed in 1.13s

Pipeline      : workforce_data_pipeline
Status        : SUCCESS
Validation    : PASSED (100.0/100)
Quality Score : 99.63/100 (PASSED)
Lineage Steps : 4
Audit Events  : 5
```

---

## License

MIT — see [LICENSE](LICENSE).

> Author: Sunil Kumar Mudusu
