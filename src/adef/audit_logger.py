import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LOG_PATH = Path("adef_audit.jsonl")


def log_event(
    action: str,
    dataset_id: str,
    status: str,
    detail: str,
    actor: str = "adef-pipeline",
    log_path: Path = DEFAULT_LOG_PATH,
) -> dict:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "action": action,
        "dataset_id": dataset_id,
        "status": status,
        "detail": detail,
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    return event


def read_events(
    dataset_id: str | None = None,
    log_path: Path = DEFAULT_LOG_PATH,
) -> list[dict]:
    if not log_path.exists():
        return []
    events = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                event = json.loads(line)
                if dataset_id is None or event.get("dataset_id") == dataset_id:
                    events.append(event)
    return events
