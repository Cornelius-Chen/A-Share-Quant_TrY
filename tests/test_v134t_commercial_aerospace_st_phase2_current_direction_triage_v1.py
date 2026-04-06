from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134t_commercial_aerospace_st_phase2_current_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for script_name in [
        "run_v134q_commercial_aerospace_broader_hit_mild_block_audit_v1.py",
        "run_v134s_commercial_aerospace_phase2_current_shadow_stack_v1.py",
        "run_v134t_commercial_aerospace_st_phase2_current_direction_triage_v1.py",
    ]:
        subprocess.run([sys.executable, str(repo_root / "scripts" / script_name)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134t_commercial_aerospace_st_phase2_current_direction_triage_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["authoritative_status"] == "freeze_current_phase2_shadow_stack_and_keep_all_session_and_replay_blocked"
    rows = {row["component"]: row["status"] for row in report["triage_rows"]}
    assert rows["current_phase2_wider_reference"] == "frozen"
    assert rows["all_session_widening"] == "still_blocked"
    assert rows["phase3_replay_lane"] == "still_blocked"
