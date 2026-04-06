from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134al_commercial_aerospace_ak_local_veto_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    subprocess.run(
        ["python", "scripts/run_v134ak_commercial_aerospace_rebound_cost_local_veto_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134al_commercial_aerospace_ak_local_veto_direction_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )

    report_path = (
        repo_root
        / "reports"
        / "analysis"
        / "v134al_commercial_aerospace_ak_local_veto_direction_triage_v1.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert "authoritative_status" in report["summary"]
