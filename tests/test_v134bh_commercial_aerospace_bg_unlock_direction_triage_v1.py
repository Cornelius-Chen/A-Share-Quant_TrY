from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134bh_commercial_aerospace_bg_unlock_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134bg_commercial_aerospace_board_revival_unlock_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134bh_commercial_aerospace_bg_unlock_direction_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134bh_commercial_aerospace_bg_unlock_direction_triage_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert (
        payload["summary"]["authoritative_status"]
        == "freeze_board_revival_unlock_supervision_and_continue_board_level_unlock_governance_only"
    )
