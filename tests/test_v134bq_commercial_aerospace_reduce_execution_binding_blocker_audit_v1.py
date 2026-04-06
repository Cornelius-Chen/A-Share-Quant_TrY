from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134bq_commercial_aerospace_reduce_execution_binding_blocker_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134bq_commercial_aerospace_reduce_execution_binding_blocker_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134bq_commercial_aerospace_reduce_execution_binding_blocker_audit_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["blocker_count"] == 4
    assert payload["blocker_rows"][0]["blocker_name"] == "point_in_time_intraday_visibility"
    assert payload["blocker_rows"][-1]["blocker_name"] == "reentry_execution_surface"
