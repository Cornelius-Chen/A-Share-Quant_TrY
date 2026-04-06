from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134aw_commercial_aerospace_post_exit_reentry_seed_registry_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134au_commercial_aerospace_post_exit_rebound_pattern_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134aw_commercial_aerospace_post_exit_reentry_seed_registry_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134aw_commercial_aerospace_post_exit_reentry_seed_registry_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["registry_count"] >= 1

