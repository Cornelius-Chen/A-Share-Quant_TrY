from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134ba_commercial_aerospace_post_exit_reentry_timing_supervision_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134ay_commercial_aerospace_post_exit_reentry_supervision_spec_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134ba_commercial_aerospace_post_exit_reentry_timing_supervision_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134ba_commercial_aerospace_post_exit_reentry_timing_supervision_audit_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["seed_count"] == 3
    assert payload["summary"]["same_day_chase_block_seed_count"] == 3
    delayed_rows = [row for row in payload["family_rows"] if row["reentry_family"] == "delayed_rebound_reentry_gap"]
    assert delayed_rows
    assert delayed_rows[0]["earliest_rebuild_watch_day"] == 3
