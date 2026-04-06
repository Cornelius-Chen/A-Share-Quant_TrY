from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134bi_commercial_aerospace_hierarchy_governance_spec_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134bk_commercial_aerospace_local_only_rebound_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134bi_commercial_aerospace_hierarchy_governance_spec_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = repo_root / "reports" / "analysis" / "v134bi_commercial_aerospace_hierarchy_governance_spec_v1.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["hierarchy_level_count"] == 4
    assert payload["hierarchy_rows"][0]["state_name"] == "board_cooling_lockout"
