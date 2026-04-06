from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134i_commercial_aerospace_phase2_seed_supervision_review_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "run_v134i_commercial_aerospace_phase2_seed_supervision_review_v1.py"

    subprocess.run([sys.executable, str(script_path)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134i_commercial_aerospace_phase2_seed_supervision_review_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["phase2_supervision_verdict"] == "reasonable_with_targeted_optimization_space"
    assert report["summary"]["recommended_widening_surface"] == "broader_hit_sessions_only"
    assert report["summary"]["recommended_widening_tiers"] == ["reversal_watch", "severe_override_positive"]
    assert report["summary"]["mild_execution_promotable"] is False

    component_status = {row["component"]: row["status"] for row in report["component_rows"]}
    assert component_status["seed_determinism"] == "reasonable"
    assert component_status["reversal_tier_value"] == "strongest_phase2_candidate"
    assert component_status["mild_tier_execution"] == "not_promotable_for_sell_execution"
