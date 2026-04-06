from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134ad_commercial_aerospace_ac_reversal_fraction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    subprocess.run(
        ["python", "scripts/run_v134ac_commercial_aerospace_reversal_sell_fraction_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134ad_commercial_aerospace_ac_reversal_fraction_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )

    report_path = (
        repo_root / "reports" / "analysis" / "v134ad_commercial_aerospace_ac_reversal_fraction_triage_v1.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert "authoritative_status" in report["summary"]
    rows = {row["component"]: row["status"] for row in report["triage_rows"]}
    assert rows["all_session_widening"] == "still_blocked"
    assert rows["phase3_replay_lane"] == "still_blocked"
