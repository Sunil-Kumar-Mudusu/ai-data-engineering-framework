#!/usr/bin/env python3
"""
End-to-end demonstration of the AI Data Engineering Framework.

Based on: Mudusu, S. K. (2025). AI Data Engineering Framework.
JRTCSE — Journal of Research Trends in Computer Science and Engineering, Vol. 13, No. 1.
https://jrtcse.com/index.php/home/article/view/JRTCSE.2025.13.1.12
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from adef.pipeline_runner import run_pipeline

EXAMPLES_DIR = Path(__file__).parent
CONFIG_FILE = EXAMPLES_DIR / "pipeline_config.yaml"
DATA_FILE = EXAMPLES_DIR / "sample_input.csv"
DB_PATH = EXAMPLES_DIR / "pipeline_run.db"
LOG_PATH = EXAMPLES_DIR / "pipeline_audit.jsonl"
LINEAGE_PATH = EXAMPLES_DIR / "pipeline_lineage.jsonl"

for artifact in [DB_PATH, LOG_PATH, LINEAGE_PATH]:
    if artifact.exists():
        artifact.unlink()


def sep():
    print("=" * 60)


def main():
    sep()
    print("  AI Data Engineering Framework — Pipeline Run")
    sep()
    print()

    summary = run_pipeline(
        config_path=CONFIG_FILE,
        input_path=DATA_FILE,
        db_path=DB_PATH,
        lineage_path=LINEAGE_PATH,
        log_path=LOG_PATH,
    )

    stages = summary["stages"]

    print(f"  Pipeline   : {summary['pipeline_name']}")
    print(f"  Run ID     : {summary['run_id']}")
    print(f"  Dataset ID : {summary['dataset_id']}")
    print(f"  Source     : {summary['source_name']}")
    print()

    print("[1] Ingestion")
    ing = stages["ingestion"]
    print(f"    rows       : {ing['rows']}")
    print(f"    columns    : {ing['columns']}")
    print(f"    checksum   : {ing['checksum']}...")
    print()

    print("[2] Schema Validation")
    val = stages["validation"]
    print(f"    passed     : {val['passed']}")
    print(f"    score      : {val['score']}/100")
    print(f"    checks run : {val['checks']}")
    print()

    print("[3] Transformation")
    trn = stages["transformation"]
    print(f"    rules applied  : {trn['rules_applied']}")
    print(f"    output columns : {trn['output_columns']}")
    print()

    print("[4] Data Quality")
    qlt = stages["quality"]
    print(f"    passed     : {qlt['passed']}")
    print(f"    score      : {qlt['score']}/100")
    print(f"    missing    : {qlt['missing_pct']}%")
    print(f"    duplicates : {qlt['duplicate_count']} rows")
    print()

    sep()
    print("  VERIFICATION SUMMARY")
    sep()
    print(f"  Pipeline      : {summary['pipeline_name']}")
    print(f"  Status        : {summary['status'].upper()}")
    print(f"  Validation    : {'PASSED' if val['passed'] else 'WARNINGS'} ({val['score']}/100)")
    print(f"  Quality Score : {qlt['score']}/100 ({'PASSED' if qlt['passed'] else 'WARNINGS'})")
    print(f"  Lineage Steps : {summary['lineage_steps']}")
    print(f"  Audit Events  : {summary['audit_events'] + 1}")
    sep()


if __name__ == "__main__":
    main()
