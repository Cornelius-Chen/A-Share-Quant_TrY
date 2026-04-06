from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134hp_commercial_aerospace_ho_crowding_contrast_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134hp_commercial_aerospace_ho_crowding_contrast_direction_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134hp_commercial_aerospace_ho_crowding_contrast_direction_triage_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["crowding_like_shelter_rebound_count"] == 2
    assert payload["summary"]["locked_board_weak_repair_count"] == 1
    assert payload["summary"]["authoritative_status"] == "retain_crowding_vs_weak_repair_contrast_and_do_not_treat_crowded_symbol_strength_as_board_restart"
