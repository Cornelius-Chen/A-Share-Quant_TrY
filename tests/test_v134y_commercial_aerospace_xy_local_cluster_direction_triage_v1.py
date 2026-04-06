from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134y_commercial_aerospace_xy_local_cluster_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for script_name in [
        "run_v134q_commercial_aerospace_broader_hit_mild_block_audit_v1.py",
        "run_v134x_commercial_aerospace_reversal_late_severe_block_audit_v1.py",
        "run_v134y_commercial_aerospace_xy_local_cluster_direction_triage_v1.py",
    ]:
        subprocess.run([sys.executable, str(repo_root / "scripts" / script_name)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134y_commercial_aerospace_xy_local_cluster_direction_triage_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["authoritative_status"] == "promote_reversal_late_severe_block_inside_current_wider_reference"
    rows = {row["component"]: row["status"] for row in report["triage_rows"]}
    assert rows["reversal_late_severe_block"] == "promote_inside_current_wider_reference"
    assert rows["phase3_replay_lane"] == "still_blocked"
