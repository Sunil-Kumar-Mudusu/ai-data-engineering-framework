import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB_PATH = Path("adef_metadata.db")


def _conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_store(db_path: Path = DEFAULT_DB_PATH) -> None:
    with _conn(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id        TEXT NOT NULL,
                pipeline_name TEXT,
                dataset_id    TEXT,
                source_name   TEXT,
                status        TEXT,
                raw_summary   TEXT,
                created_at    TEXT
            );
            CREATE TABLE IF NOT EXISTS dataset_metadata (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id          TEXT NOT NULL,
                source_name         TEXT,
                row_count           INTEGER,
                column_count        INTEGER,
                checksum            TEXT,
                ingestion_timestamp TEXT,
                raw_metadata        TEXT,
                created_at          TEXT
            );
            CREATE TABLE IF NOT EXISTS validation_results (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id TEXT NOT NULL,
                passed     INTEGER,
                score      REAL,
                raw_result TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS quality_results (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id    TEXT NOT NULL,
                quality_score REAL,
                passed        INTEGER,
                raw_result    TEXT,
                created_at    TEXT
            );
        """)


def store_run(run_id: str, summary: dict, db_path: Path = DEFAULT_DB_PATH) -> None:
    with _conn(db_path) as conn:
        conn.execute(
            """INSERT INTO pipeline_runs
               (run_id, pipeline_name, dataset_id, source_name, status, raw_summary, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (run_id, summary.get("pipeline_name"), summary.get("dataset_id"),
             summary.get("source_name"), summary.get("status"), json.dumps(summary), _now()),
        )


def store_metadata(metadata: dict, db_path: Path = DEFAULT_DB_PATH) -> None:
    with _conn(db_path) as conn:
        conn.execute(
            """INSERT INTO dataset_metadata
               (dataset_id, source_name, row_count, column_count, checksum,
                ingestion_timestamp, raw_metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (metadata.get("dataset_id"), metadata.get("source_name"),
             metadata.get("row_count"), metadata.get("column_count"),
             metadata.get("checksum"), metadata.get("ingestion_timestamp"),
             json.dumps(metadata), _now()),
        )


def store_validation(dataset_id: str, result: dict, db_path: Path = DEFAULT_DB_PATH) -> None:
    with _conn(db_path) as conn:
        conn.execute(
            """INSERT INTO validation_results (dataset_id, passed, score, raw_result, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (dataset_id, int(result.get("passed", False)),
             result.get("score"), json.dumps(result), _now()),
        )


def store_quality(dataset_id: str, result: dict, db_path: Path = DEFAULT_DB_PATH) -> None:
    with _conn(db_path) as conn:
        conn.execute(
            """INSERT INTO quality_results
               (dataset_id, quality_score, passed, raw_result, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (dataset_id, result.get("quality_score"),
             int(result.get("passed", False)), json.dumps(result), _now()),
        )


def query_runs(db_path: Path = DEFAULT_DB_PATH) -> list[dict]:
    with _conn(db_path) as conn:
        rows = conn.execute(
            """SELECT run_id, pipeline_name, source_name, status, created_at
               FROM pipeline_runs ORDER BY created_at DESC"""
        ).fetchall()
    return [dict(r) for r in rows]


def query_datasets(db_path: Path = DEFAULT_DB_PATH) -> list[dict]:
    with _conn(db_path) as conn:
        rows = conn.execute(
            """SELECT dataset_id, source_name, row_count, column_count, ingestion_timestamp
               FROM dataset_metadata ORDER BY created_at DESC"""
        ).fetchall()
    return [dict(r) for r in rows]
