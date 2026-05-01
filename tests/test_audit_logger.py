import pytest

from adef.audit_logger import log_event, read_events


@pytest.fixture()
def log_file(tmp_path):
    return tmp_path / "audit.jsonl"


def test_log_creates_file(log_file):
    log_event("ingest", "ds-1", "success", "Loaded data", log_path=log_file)
    assert log_file.exists()


def test_log_and_read(log_file):
    log_event("ingest", "ds-1", "success", "Loaded data", log_path=log_file)
    events = read_events("ds-1", log_file)
    assert len(events) == 1


def test_event_fields(log_file):
    log_event("validate", "ds-1", "warning", "Score low", log_path=log_file)
    event = read_events("ds-1", log_file)[0]
    assert event["action"] == "validate"
    assert event["dataset_id"] == "ds-1"
    assert event["status"] == "warning"
    assert event["detail"] == "Score low"
    assert "timestamp" in event
    assert "actor" in event


def test_multiple_events(log_file):
    for i in range(4):
        log_event(f"stage_{i}", "ds-1", "success", f"msg {i}", log_path=log_file)
    events = read_events("ds-1", log_file)
    assert len(events) == 4


def test_filtered_by_dataset_id(log_file):
    log_event("ingest", "ds-A", "success", "A", log_path=log_file)
    log_event("ingest", "ds-B", "success", "B", log_path=log_file)
    events = read_events("ds-A", log_file)
    assert len(events) == 1
    assert events[0]["dataset_id"] == "ds-A"


def test_default_actor_present(log_file):
    log_event("ingest", "ds-1", "success", "msg", log_path=log_file)
    event = read_events("ds-1", log_file)[0]
    assert event["actor"] == "adef-pipeline"


def test_no_events_returns_empty(log_file):
    log_event("ingest", "ds-X", "success", "msg", log_path=log_file)
    events = read_events("ds-Y", log_file)
    assert events == []
