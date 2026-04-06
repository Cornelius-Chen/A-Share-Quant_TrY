from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134u_commercial_aerospace_phase2_wider_reference_attribution_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for script_name in [
        "run_v134q_commercial_aerospace_broader_hit_mild_block_audit_v1.py",
        "run_v134u_commercial_aerospace_phase2_wider_reference_attribution_v1.py",
    ]:
        subprocess.run([sys.executable, str(repo_root / "scripts" / script_name)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134u_commercial_aerospace_phase2_wider_reference_attribution_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["session_count"] == 24
    assert report["summary"]["same_day_loss_avoided_total"] > 0
    assert report["summary"]["best_symbol"] != ""
    assert report["summary"]["best_month_bucket"] != ""
