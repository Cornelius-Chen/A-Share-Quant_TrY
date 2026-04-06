from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134bt_commercial_aerospace_bs_sell_side_binding_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134bs_commercial_aerospace_sell_side_binding_readiness_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134bt_commercial_aerospace_bs_sell_side_binding_direction_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134bt_commercial_aerospace_bs_sell_side_binding_direction_triage_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert (
        payload["summary"]["authoritative_status"]
        == "freeze_sell_side_binding_readiness_and_build_only_missing_binding_surfaces"
    )
