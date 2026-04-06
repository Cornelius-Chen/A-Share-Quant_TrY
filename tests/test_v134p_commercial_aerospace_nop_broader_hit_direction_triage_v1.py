from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134p_commercial_aerospace_nop_broader_hit_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for script_name in [
        "run_v134l_commercial_aerospace_intraday_broader_hit_simulator_v1.py",
        "run_v134n_commercial_aerospace_broader_hit_simulator_attribution_v1.py",
        "run_v134o_commercial_aerospace_broader_hit_supervision_failure_review_v1.py",
        "run_v134p_commercial_aerospace_nop_broader_hit_direction_triage_v1.py",
    ]:
        subprocess.run([sys.executable, str(repo_root / "scripts" / script_name)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134p_commercial_aerospace_nop_broader_hit_direction_triage_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["authoritative_status"] == "retain_broader_hit_phase2_lane_but_tighten_predicted_mild_execution_boundary_next"
    rows = {row["component"]: row["status"] for row in report["triage_rows"]}
    assert rows["broader_hit_widening_value"] == "retain_with_refinement"
    assert rows["predicted_mild_session_execution"] == "tighten_next"
    assert rows["phase3_replay_lane"] == "still_blocked"
