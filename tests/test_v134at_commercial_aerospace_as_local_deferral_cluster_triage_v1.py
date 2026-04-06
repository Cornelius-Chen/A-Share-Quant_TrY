from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134at_commercial_aerospace_as_local_deferral_cluster_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134ao_commercial_aerospace_local_reversal_deferral_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134as_commercial_aerospace_local_deferral_cluster_singularity_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134at_commercial_aerospace_as_local_deferral_cluster_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134at_commercial_aerospace_as_local_deferral_cluster_triage_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["authoritative_status"] in {
        "freeze_current_local_deferral_and_stop_same_family_search",
        "keep_searching_same_family_local_deferrals",
    }
