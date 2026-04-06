from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134am_commercial_aerospace_local_veto_experiment_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    subprocess.run(
        ["python", "scripts/run_v134am_commercial_aerospace_local_veto_experiment_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )

    report_path = (
        repo_root / "reports" / "analysis" / "v134am_commercial_aerospace_local_veto_experiment_audit_v1.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["impacted_session_count"] == 2

