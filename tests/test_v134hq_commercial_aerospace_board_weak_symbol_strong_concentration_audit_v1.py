from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134hq_commercial_aerospace_board_weak_symbol_strong_concentration_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134hq_commercial_aerospace_board_weak_symbol_strong_concentration_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root
        / "reports"
        / "analysis"
        / "v134hq_commercial_aerospace_board_weak_symbol_strong_concentration_audit_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["module_member_count"] == 3
    assert payload["summary"]["module_member_symbols"] == ["002361", "300342", "603601"]
    contrast = {row["contrast_name"]: row for row in payload["contrast_rows"]}
    assert contrast["peak_proximity_vs_other_negative_labels"]["mean_gap"] > 0.09
    assert contrast["avg_turnover_vs_other_negative_labels"]["mean_gap"] > 2.0

