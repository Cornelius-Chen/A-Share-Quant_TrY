from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134bn_commercial_aerospace_bm_expectancy_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134bn_commercial_aerospace_bm_expectancy_direction_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134bn_commercial_aerospace_bm_expectancy_direction_triage_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert (
        payload["summary"]["authoritative_status"]
        == "freeze_board_expectancy_supervision_and_use_expectancy_as_board_level_reduce_context"
    )
