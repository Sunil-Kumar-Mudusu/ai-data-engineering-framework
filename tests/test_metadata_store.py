import pytest

from adef.metadata_store import (
    initialize_store,
    query_datasets,
    query_runs,
    store_metadata,
    store_quality,
    store_run,
    store_validation,
)


@pytest.fixture()
def db(tmp_path):
    path = tmp_path / "test.db"
    initialize_store(path)
    return path


def test_initialize_creates_file(tmp_path):
    path = tmp_path / "new.db"
    assert not path.exists()
    initialize_store(path)
    assert path.exists()


def test_store_and_query_run(db):
    summary = {
        "pipeline_name": "test_pipeline",
        "dataset_id": "ds-001",
        "source_name": "test.csv",
        "status": "success",
    }
    store_run("run-001", summary, db)
    runs = query_runs(db)
    assert len(runs) == 1
    assert runs[0]["run_id"] == "run-001"
    assert runs[0]["pipeline_name"] == "test_pipeline"
    assert runs[0]["status"] == "success"


def test_store_and_query_metadata(db):
    meta = {
        "dataset_id": "ds-002",
        "source_name": "data.csv",
        "row_count": 100,
        "column_count": 5,
        "checksum": "abcd1234abcd1234",
        "ingestion_timestamp": "2026-01-01T00:00:00+00:00",
    }
    store_metadata(meta, db)
    datasets = query_datasets(db)
    assert len(datasets) == 1
    assert datasets[0]["dataset_id"] == "ds-002"
    assert datasets[0]["row_count"] == 100


def test_store_validation(db):
    result = {"passed": True, "score": 95.0, "total_checks": 5, "issues": []}
    store_validation("ds-003", result, db)


def test_store_quality(db):
    result = {"quality_score": 88.5, "passed": True, "missing_pct": 2.0, "duplicate_count": 0}
    store_quality("ds-004", result, db)


def test_multiple_runs(db):
    for i in range(3):
        store_run(
            f"run-{i}",
            {"pipeline_name": "p", "dataset_id": f"ds-{i}", "source_name": "f.csv", "status": "success"},
            db,
        )
    runs = query_runs(db)
    assert len(runs) == 3


def test_query_runs_empty(db):
    runs = query_runs(db)
    assert runs == []


def test_query_datasets_empty(db):
    datasets = query_datasets(db)
    assert datasets == []
