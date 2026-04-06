from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134ho_commercial_aerospace_crowding_vs_weak_repair_contrast_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134ho_commercial_aerospace_crowding_vs_weak_repair_contrast_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134ho_commercial_aerospace_crowding_vs_weak_repair_contrast_audit_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["crowding_like_shelter_rebound_count"] == 2
    assert payload["summary"]["locked_board_weak_repair_count"] == 1
    assert payload["summary"]["peak_proximity_gap"] > 0.15
    assert payload["summary"]["avg_turnover_rate_f_gap"] > 3.0
    assert payload["summary"]["max_turnover_rate_f_gap"] > 15.0

