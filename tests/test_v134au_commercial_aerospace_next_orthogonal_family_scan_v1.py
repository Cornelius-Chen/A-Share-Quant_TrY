from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134au_commercial_aerospace_next_orthogonal_family_scan_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134au_commercial_aerospace_next_orthogonal_family_scan_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = repo_root / "reports" / "analysis" / "v134au_commercial_aerospace_next_orthogonal_family_scan_v1.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["remaining_rebound_cost_case_count"] >= 3
    assert payload["summary"]["best_remaining_rebound_cost_hit_count"] >= 2

