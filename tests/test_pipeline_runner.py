from pathlib import Path

import pytest

from adef.pipeline_runner import run_pipeline

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


@pytest.fixture()
def artifacts(tmp_path):
    return {
        "config": EXAMPLES / "pipeline_config.yaml",
        "data": EXAMPLES / "sample_input.csv",
        "db": tmp_path / "run.db",
        "lineage": tmp_path / "lineage.jsonl",
        "log": tmp_path / "audit.jsonl",
    }


def test_run_pipeline_returns_dict(artifacts):
    result = run_pipeline(
        config_path=artifacts["config"],
        input_path=artifacts["data"],
        db_path=artifacts["db"],
        lineage_path=artifacts["lineage"],
        log_path=artifacts["log"],
    )
    assert isinstance(result, dict)


def test_summary_keys(artifacts):
    summary = run_pipeline(
        config_path=artifacts["config"],
        input_path=artifacts["data"],
        db_path=artifacts["db"],
        lineage_path=artifacts["lineage"],
        log_path=artifacts["log"],
    )
    for key in ("run_id", "pipeline_name", "dataset_id", "source_name", "status", "stages"):
        assert key in summary


def test_pipeline_status_success(artifacts):
    summary = run_pipeline(
        config_path=artifacts["config"],
        input_path=artifacts["data"],
        db_path=artifacts["db"],
        lineage_path=artifacts["lineage"],
        log_path=artifacts["log"],
    )
    assert summary["status"] == "success"


def test_ingestion_stage(artifacts):
    summary = run_pipeline(
        config_path=artifacts["config"],
        input_path=artifacts["data"],
        db_path=artifacts["db"],
        lineage_path=artifacts["lineage"],
        log_path=artifacts["log"],
    )
    ing = summary["stages"]["ingestion"]
    assert ing["rows"] == 18
    assert ing["columns"] > 0
    assert ing["checksum"]


def test_validation_stage(artifacts):
    summary = run_pipeline(
        config_path=artifacts["config"],
        input_path=artifacts["data"],
        db_path=artifacts["db"],
        lineage_path=artifacts["lineage"],
        log_path=artifacts["log"],
    )
    val = summary["stages"]["validation"]
    assert "passed" in val
    assert 0 <= val["score"] <= 100


def test_transformation_stage(artifacts):
    summary = run_pipeline(
        config_path=artifacts["config"],
        input_path=artifacts["data"],
        db_path=artifacts["db"],
        lineage_path=artifacts["lineage"],
        log_path=artifacts["log"],
    )
    trn = summary["stages"]["transformation"]
    assert trn["rules_applied"] > 0
    assert trn["output_columns"] > 0


def test_quality_stage(artifacts):
    summary = run_pipeline(
        config_path=artifacts["config"],
        input_path=artifacts["data"],
        db_path=artifacts["db"],
        lineage_path=artifacts["lineage"],
        log_path=artifacts["log"],
    )
    qlt = summary["stages"]["quality"]
    assert 0 <= qlt["score"] <= 100
    assert qlt["duplicate_count"] >= 0


def test_artifacts_created(artifacts):
    run_pipeline(
        config_path=artifacts["config"],
        input_path=artifacts["data"],
        db_path=artifacts["db"],
        lineage_path=artifacts["lineage"],
        log_path=artifacts["log"],
    )
    assert artifacts["db"].exists()
    assert artifacts["lineage"].exists()
    assert artifacts["log"].exists()


def test_lineage_steps(artifacts):
    summary = run_pipeline(
        config_path=artifacts["config"],
        input_path=artifacts["data"],
        db_path=artifacts["db"],
        lineage_path=artifacts["lineage"],
        log_path=artifacts["log"],
    )
    assert summary["lineage_steps"] == 4


def test_pipeline_name_from_config(artifacts):
    summary = run_pipeline(
        config_path=artifacts["config"],
        input_path=artifacts["data"],
        db_path=artifacts["db"],
        lineage_path=artifacts["lineage"],
        log_path=artifacts["log"],
    )
    assert summary["pipeline_name"] == "workforce_data_pipeline"
