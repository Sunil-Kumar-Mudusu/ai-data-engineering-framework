import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LINEAGE_PATH = Path("adef_lineage.jsonl")


def record_lineage(
    dataset_id: str,
    step: str,
    inputs: list[str],
    outputs: list[str],
    metadata: dict | None = None,
    lineage_path: Path = DEFAULT_LINEAGE_PATH,
) -> dict:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset_id": dataset_id,
        "step": step,
        "inputs": inputs,
        "outputs": outputs,
        "metadata": metadata or {},
    }
    with open(lineage_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record


def get_lineage(dataset_id: str, lineage_path: Path = DEFAULT_LINEAGE_PATH) -> list[dict]:
    if not lineage_path.exists():
        return []
    records = []
    with open(lineage_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                if rec.get("dataset_id") == dataset_id:
                    records.append(rec)
    return records
