from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134bl_commercial_aerospace_bk_local_only_rebound_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134bk_commercial_aerospace_local_only_rebound_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134bl_commercial_aerospace_bk_local_only_rebound_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134bl_commercial_aerospace_bk_local_only_rebound_triage_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["authoritative_status"] == "freeze_local_only_rebound_guard_and_keep_board_unlock_strict"
