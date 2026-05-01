import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .exceptions import IngestionError


def ingest_csv(path: str | Path) -> tuple[pd.DataFrame, dict]:
    path = Path(path)
    if not path.exists():
        raise IngestionError(f"File not found: {path}")
    if path.suffix.lower() != ".csv":
        raise IngestionError(f"Expected .csv file, got: {path.suffix}")

    raw = path.read_bytes()
    checksum = hashlib.sha256(raw).hexdigest()[:16]
    try:
        df = pd.read_csv(path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        raise IngestionError(f"Failed to parse CSV: {exc}") from exc
    if df.empty and len(df.columns) == 0:
        raise IngestionError(f"CSV file is empty: {path}")

    metadata = {
        "dataset_id": str(uuid.uuid4()),
        "source_name": path.name,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
        "source_path": str(path),
        "checksum": checksum,
        "file_size_bytes": path.stat().st_size,
    }
    return df, metadata
