import uuid
from pathlib import Path

from .audit_logger import log_event
from .config import load_yaml
from .ingestion import ingest_csv
from .lineage_tracker import record_lineage
from .metadata_store import (
    initialize_store,
    store_metadata,
    store_quality,
    store_run,
    store_validation,
)
from .quality_engine import run_quality_checks
from .transformation import apply_transformations
from .validation import validate_schema


def run_pipeline(
    config_path: str | Path,
    input_path: str | Path,
    db_path: Path | None = None,
    lineage_path: Path | None = None,
    log_path: Path | None = None,
) -> dict:
    config = load_yaml(config_path)
    pipeline_name = config.get("pipeline", {}).get("name", "unnamed_pipeline")
    run_id = str(uuid.uuid4())

    db_path = db_path or Path("adef_metadata.db")
    lineage_path = lineage_path or Path("adef_lineage.jsonl")
    log_path = log_path or Path("adef_audit.jsonl")

    initialize_store(db_path)

    # Stage 1: Ingestion
    df, metadata = ingest_csv(input_path)
    dataset_id = metadata["dataset_id"]
    store_metadata(metadata, db_path)
    log_event("ingest", dataset_id, "success",
              f"Loaded {metadata['row_count']} rows from {metadata['source_name']}",
              log_path=log_path)
    record_lineage(dataset_id, "ingestion", [str(input_path)], ["raw_dataset"],
                   {"row_count": metadata["row_count"]}, lineage_path=lineage_path)

    # Stage 2: Validation
    validation_result = validate_schema(df, config)
    store_validation(dataset_id, validation_result, db_path)
    log_event("validate", dataset_id,
              "success" if validation_result["passed"] else "warning",
              f"Validation score: {validation_result['score']}/100", log_path=log_path)
    record_lineage(dataset_id, "validation", ["raw_dataset"], ["validated_dataset"],
                   {"passed": validation_result["passed"], "score": validation_result["score"]},
                   lineage_path=lineage_path)

    # Stage 3: Transformation
    df_transformed, transform_log = apply_transformations(df, config)
    applied = sum(1 for t in transform_log if t.get("status") == "applied")
    log_event("transform", dataset_id, "success",
              f"{applied} transformation(s) applied", log_path=log_path)
    record_lineage(dataset_id, "transformation", ["validated_dataset"], ["transformed_dataset"],
                   {"rules_applied": applied, "output_columns": len(df_transformed.columns)},
                   lineage_path=lineage_path)

    # Stage 4: Quality checks
    quality_result = run_quality_checks(df_transformed, config)
    store_quality(dataset_id, quality_result, db_path)
    log_event("quality_check", dataset_id,
              "success" if quality_result["passed"] else "warning",
              f"Quality score: {quality_result['quality_score']}/100", log_path=log_path)
    record_lineage(dataset_id, "quality_check", ["transformed_dataset"], ["quality_checked_dataset"],
                   {"score": quality_result["quality_score"], "passed": quality_result["passed"]},
                   lineage_path=lineage_path)

    summary = {
        "run_id": run_id,
        "pipeline_name": pipeline_name,
        "dataset_id": dataset_id,
        "source_name": metadata["source_name"],
        "status": "success",
        "stages": {
            "ingestion": {
                "rows": metadata["row_count"],
                "columns": metadata["column_count"],
                "checksum": metadata["checksum"],
            },
            "validation": {
                "passed": validation_result["passed"],
                "score": validation_result["score"],
                "checks": validation_result["total_checks"],
            },
            "transformation": {
                "rules_applied": applied,
                "output_columns": len(df_transformed.columns),
            },
            "quality": {
                "passed": quality_result["passed"],
                "score": quality_result["quality_score"],
                "missing_pct": quality_result["missing_pct"],
                "duplicate_count": quality_result["duplicate_count"],
            },
        },
        "lineage_steps": 4,
        "audit_events": 4,
    }

    store_run(run_id, summary, db_path)
    log_event("pipeline_complete", dataset_id, "success",
              f"Pipeline '{pipeline_name}' completed. Quality: {quality_result['quality_score']}",
              log_path=log_path)

    return summary
