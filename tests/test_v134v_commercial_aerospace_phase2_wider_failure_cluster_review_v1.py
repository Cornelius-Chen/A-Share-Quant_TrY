from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134v_commercial_aerospace_phase2_wider_failure_cluster_review_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for script_name in [
        "run_v134q_commercial_aerospace_broader_hit_mild_block_audit_v1.py",
        "run_v134v_commercial_aerospace_phase2_wider_failure_cluster_review_v1.py",
    ]:
        subprocess.run([sys.executable, str(repo_root / "scripts" / script_name)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134v_commercial_aerospace_phase2_wider_failure_cluster_review_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["negative_session_count"] >= 0
    assert report["summary"]["failure_cluster_count"] >= 1
    assert report["summary"]["top_failure_cluster"] != ""
