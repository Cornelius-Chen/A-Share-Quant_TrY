from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134r_commercial_aerospace_qr_mild_block_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for script_name in [
        "run_v134l_commercial_aerospace_intraday_broader_hit_simulator_v1.py",
        "run_v134q_commercial_aerospace_broader_hit_mild_block_audit_v1.py",
        "run_v134r_commercial_aerospace_qr_mild_block_triage_v1.py",
    ]:
        subprocess.run([sys.executable, str(repo_root / "scripts" / script_name)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134r_commercial_aerospace_qr_mild_block_triage_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["authoritative_status"] == "promote_predicted_mild_block_inside_broader_hit_phase2_lane"
    rows = {row["component"]: row["status"] for row in report["triage_rows"]}
    assert rows["predicted_mild_boundary_change"] == "promote_inside_phase_2"
    assert rows["phase3_replay_lane"] == "still_blocked"
