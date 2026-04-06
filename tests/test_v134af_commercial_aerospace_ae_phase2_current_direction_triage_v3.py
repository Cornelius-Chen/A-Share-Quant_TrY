from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134af_commercial_aerospace_ae_phase2_current_direction_triage_v3() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    subprocess.run(
        ["python", "scripts/run_v134ae_commercial_aerospace_phase2_current_shadow_stack_v3.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134af_commercial_aerospace_ae_phase2_current_direction_triage_v3.py"],
        cwd=repo_root,
        check=True,
    )

    report_path = (
        repo_root
        / "reports"
        / "analysis"
        / "v134af_commercial_aerospace_ae_phase2_current_direction_triage_v3.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["authoritative_status"] == "freeze_phase2_shadow_stack_v3_and_keep_all_session_and_replay_blocked"
    rows = {row["component"]: row["status"] for row in report["triage_rows"]}
    assert rows["multi_stage_sell_ladder_refinement"] == "promoted_inside_current_wider_reference"
