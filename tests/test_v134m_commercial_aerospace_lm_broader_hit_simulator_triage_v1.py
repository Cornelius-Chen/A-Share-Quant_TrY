from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134m_commercial_aerospace_lm_broader_hit_simulator_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for script_name in [
        "run_v134l_commercial_aerospace_intraday_broader_hit_simulator_v1.py",
        "run_v134m_commercial_aerospace_lm_broader_hit_simulator_triage_v1.py",
    ]:
        subprocess.run([sys.executable, str(repo_root / "scripts" / script_name)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134m_commercial_aerospace_lm_broader_hit_simulator_triage_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["authoritative_status"] == "retain_broader_hit_widening_inside_phase_2_but_keep_replay_blocked"
    rows = {row["component"]: row["status"] for row in report["triage_rows"]}
    assert rows["broader_hit_phase2_widening"] == "retained_inside_phase_2"
    assert rows["mild_execution_boundary"] == "preserved"
    assert rows["replay_boundary"] == "still_blocked"
