from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134w_commercial_aerospace_uvw_phase2_wider_supervision_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for script_name in [
        "run_v134q_commercial_aerospace_broader_hit_mild_block_audit_v1.py",
        "run_v134u_commercial_aerospace_phase2_wider_reference_attribution_v1.py",
        "run_v134v_commercial_aerospace_phase2_wider_failure_cluster_review_v1.py",
        "run_v134w_commercial_aerospace_uvw_phase2_wider_supervision_triage_v1.py",
    ]:
        subprocess.run([sys.executable, str(repo_root / "scripts" / script_name)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134w_commercial_aerospace_uvw_phase2_wider_supervision_triage_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["authoritative_status"] == "retain_current_wider_reference_and_shift_next_to_local_failure_cluster_supervision"
    rows = {row["component"]: row["status"] for row in report["triage_rows"]}
    assert rows["current_wider_reference"] == "retain"
    assert rows["all_session_widening"] == "still_blocked"
    assert rows["phase3_replay_lane"] == "still_blocked"
