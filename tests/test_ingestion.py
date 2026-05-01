import hashlib
from pathlib import Path

import pandas as pd
import pytest

from adef.ingestion import ingest_csv


@pytest.fixture()
def csv_file(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("id,name,value\n1,Alice,10\n2,Bob,20\n3,Carol,30\n")
    return path


def test_returns_dataframe_and_metadata(csv_file):
    df, meta = ingest_csv(csv_file)
    assert isinstance(df, pd.DataFrame)
    assert isinstance(meta, dict)


def test_row_and_column_counts(csv_file):
    df, meta = ingest_csv(csv_file)
    assert meta["row_count"] == 3
    assert meta["column_count"] == 3
    assert len(df) == 3
    assert len(df.columns) == 3


def test_dataset_id_is_uuid(csv_file):
    import uuid
    _, meta = ingest_csv(csv_file)
    uid = uuid.UUID(meta["dataset_id"])
    assert str(uid) == meta["dataset_id"]


def test_checksum_is_hex_16(csv_file):
    _, meta = ingest_csv(csv_file)
    assert len(meta["checksum"]) == 16
    int(meta["checksum"], 16)


def test_checksum_matches_file(csv_file):
    raw = csv_file.read_bytes()
    expected = hashlib.sha256(raw).hexdigest()[:16]
    _, meta = ingest_csv(csv_file)
    assert meta["checksum"] == expected


def test_source_name(csv_file):
    _, meta = ingest_csv(csv_file)
    assert meta["source_name"] == csv_file.name


def test_ingestion_timestamp_present(csv_file):
    _, meta = ingest_csv(csv_file)
    assert "ingestion_timestamp" in meta
    assert meta["ingestion_timestamp"]


def test_missing_file_raises(tmp_path):
    from adef.exceptions import IngestionError
    with pytest.raises(IngestionError):
        ingest_csv(tmp_path / "nonexistent.csv")


def test_empty_csv_raises(tmp_path):
    from adef.exceptions import IngestionError
    path = tmp_path / "empty.csv"
    path.write_text("")
    with pytest.raises(IngestionError):
        ingest_csv(path)


def test_unique_dataset_ids(csv_file):
    _, m1 = ingest_csv(csv_file)
    _, m2 = ingest_csv(csv_file)
    assert m1["dataset_id"] != m2["dataset_id"]
