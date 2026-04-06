from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134o_commercial_aerospace_broader_hit_supervision_failure_review_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for script_name in [
        "run_v134l_commercial_aerospace_intraday_broader_hit_simulator_v1.py",
        "run_v134n_commercial_aerospace_broader_hit_simulator_attribution_v1.py",
        "run_v134o_commercial_aerospace_broader_hit_supervision_failure_review_v1.py",
    ]:
        subprocess.run([sys.executable, str(repo_root / "scripts" / script_name)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134o_commercial_aerospace_broader_hit_supervision_failure_review_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["negative_session_count"] > 0
    assert report["summary"]["recommended_boundary_change"] == "block_execution_for_predicted_mild_sessions_inside_broader_hit_lane"
    assert report["summary"]["mild_tier_same_day_loss_avoided_total"] < 0
