from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["unlock_worthy_count"] >= 1
    assert payload["summary"]["false_bounce_only_count"] >= 1
    assert payload["summary"]["lockout_worthy_count"] >= 1
    assert payload["summary"]["unlock_worthy_mean_forward_20d"] > 0
    assert payload["summary"]["false_bounce_only_mean_forward_20d"] < 0
