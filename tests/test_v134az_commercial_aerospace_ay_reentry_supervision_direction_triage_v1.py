from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134az_commercial_aerospace_ay_reentry_supervision_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134ay_commercial_aerospace_post_exit_reentry_supervision_spec_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134az_commercial_aerospace_ay_reentry_supervision_direction_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134az_commercial_aerospace_ay_reentry_supervision_direction_triage_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["authoritative_status"] == "freeze_reentry_supervision_spec_and_continue_seed_level_reentry_supervision"
