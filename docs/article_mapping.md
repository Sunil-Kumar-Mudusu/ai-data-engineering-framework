# Article Mapping

Source article: Mudusu, S. K. (2025). AI Data Engineering Framework.
*JRTCSE — Journal of Research Trends in Computer Science and Engineering*, Vol. 13, No. 1.

## Concept → Implementation

| Article Concept | Implementation |
|---|---|
| Data ingestion with integrity verification | `ingestion.py` — SHA-256 checksum, UUID dataset ID |
| Schema validation and constraint enforcement | `validation.py` — required columns, types, allowed values |
| Config-driven transformation pipeline | `transformation.py` — rename, drop, derive, normalize, cast |
| Data quality scoring | `quality_engine.py` — completeness × 0.6 + uniqueness × 0.4 |
| Lineage tracking | `lineage_tracker.py` — JSONL per-stage records |
| Audit logging | `audit_logger.py` — JSONL immutable event log |
| Metadata persistence | `metadata_store.py` — SQLite with four tables |
| Pipeline orchestration | `pipeline_runner.py` — four-stage run with summary |
| YAML-driven configuration | `config.py` — `load_yaml()` wrapper |
| Domain exception hierarchy | `exceptions.py` — `ADEFError` and stage-specific subclasses |

## Quality Scoring Formula

The article specifies quality as a weighted combination of completeness and uniqueness:

```
quality_score = completeness_score * 0.6 + uniqueness_score * 0.4

completeness_score = 100 - missing_pct
uniqueness_score   = 100 - duplicate_pct
```

This implementation directly applies that formula in `quality_engine.run_quality_checks()`.
