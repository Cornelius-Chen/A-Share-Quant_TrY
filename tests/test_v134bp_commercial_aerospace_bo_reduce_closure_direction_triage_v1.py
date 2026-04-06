from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134bp_commercial_aerospace_bo_reduce_closure_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134bo_commercial_aerospace_reduce_closure_governance_spec_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134bp_commercial_aerospace_bo_reduce_closure_direction_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134bp_commercial_aerospace_bo_reduce_closure_direction_triage_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert (
        payload["summary"]["authoritative_status"]
        == "freeze_reduce_closure_governance_and_continue_board_first_reduce_training"
    )
