import pytest

from adef.lineage_tracker import get_lineage, record_lineage


@pytest.fixture()
def lineage_file(tmp_path):
    return tmp_path / "lineage.jsonl"


def test_record_creates_file(lineage_file):
    record_lineage("ds-1", "ingestion", [], ["raw"], {}, lineage_path=lineage_file)
    assert lineage_file.exists()


def test_record_and_retrieve(lineage_file):
    record_lineage("ds-1", "ingestion", ["src.csv"], ["raw_dataset"],
                   {"row_count": 10}, lineage_path=lineage_file)
    events = get_lineage("ds-1", lineage_file)
    assert len(events) == 1
    assert events[0]["step"] == "ingestion"


def test_lineage_fields(lineage_file):
    record_lineage("ds-1", "validation", ["raw_dataset"], ["validated_dataset"],
                   {"score": 95}, lineage_path=lineage_file)
    event = get_lineage("ds-1", lineage_file)[0]
    assert "dataset_id" in event
    assert "step" in event
    assert "inputs" in event
    assert "outputs" in event
    assert "metadata" in event
    assert "timestamp" in event


def test_multiple_stages(lineage_file):
    for stage in ["ingestion", "validation", "transformation", "quality_check"]:
        record_lineage("ds-1", stage, [], [], {}, lineage_path=lineage_file)
    events = get_lineage("ds-1", lineage_file)
    assert len(events) == 4


def test_filtered_by_dataset_id(lineage_file):
    record_lineage("ds-A", "ingestion", [], [], {}, lineage_path=lineage_file)
    record_lineage("ds-B", "ingestion", [], [], {}, lineage_path=lineage_file)
    events = get_lineage("ds-A", lineage_file)
    assert len(events) == 1
    assert events[0]["dataset_id"] == "ds-A"


def test_metadata_stored(lineage_file):
    record_lineage("ds-1", "quality_check", [], [], {"score": 88.5}, lineage_path=lineage_file)
    event = get_lineage("ds-1", lineage_file)[0]
    assert event["metadata"]["score"] == 88.5


def test_no_events_returns_empty(lineage_file):
    record_lineage("ds-X", "ingestion", [], [], {}, lineage_path=lineage_file)
    events = get_lineage("ds-Y", lineage_file)
    assert events == []
