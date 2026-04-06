from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134hr_commercial_aerospace_hq_module_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134hr_commercial_aerospace_hq_module_direction_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134hr_commercial_aerospace_hq_module_direction_triage_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["module_member_count"] == 3
    assert payload["summary"]["module_member_symbols"] == ["002361", "300342", "603601"]
    assert payload["summary"]["authoritative_status"] == "retain_board_weak_symbol_strong_concentration_as_higher_level_negative_label_module"
