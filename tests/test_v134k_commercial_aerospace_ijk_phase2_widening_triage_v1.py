from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134k_commercial_aerospace_ijk_phase2_widening_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for script_name in [
        "run_v134i_commercial_aerospace_phase2_seed_supervision_review_v1.py",
        "run_v134j_commercial_aerospace_phase2_broader_hit_widening_protocol_v1.py",
        "run_v134k_commercial_aerospace_ijk_phase2_widening_triage_v1.py",
    ]:
        subprocess.run([sys.executable, str(repo_root / "scripts" / script_name)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134k_commercial_aerospace_ijk_phase2_widening_triage_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert (
        report["summary"]["authoritative_status"]
        == "approve_broader_hit_phase2_widening_with_guardrails_but_keep_all_session_and_replay_blocked"
    )
    rows = {row["component"]: row["status"] for row in report["triage_rows"]}
    assert rows["phase2_seed_training_result"] == "reasonable"
    assert rows["broader_hit_widening"] == "approved_with_guardrails"
    assert rows["all_session_widening"] == "still_blocked"
    assert rows["phase3_replay_lane"] == "still_blocked"
