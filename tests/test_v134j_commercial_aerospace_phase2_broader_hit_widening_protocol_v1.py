from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134j_commercial_aerospace_phase2_broader_hit_widening_protocol_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for script_name in [
        "run_v134i_commercial_aerospace_phase2_seed_supervision_review_v1.py",
        "run_v134j_commercial_aerospace_phase2_broader_hit_widening_protocol_v1.py",
    ]:
        subprocess.run([sys.executable, str(repo_root / "scripts" / script_name)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134j_commercial_aerospace_phase2_broader_hit_widening_protocol_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["phase2_widening_status"] == "approved_with_guardrails"
    assert report["summary"]["allowed_widening_surface"] == "broader_hit_sessions_only"
    assert report["summary"]["allowed_execution_tiers"] == ["reversal_watch", "severe_override_positive"]
    assert report["summary"]["blocked_execution_tiers"] == ["mild_override_watch"]

    rows = {row["protocol_component"]: row["status"] for row in report["protocol_rows"]}
    assert rows["widening_scope"] == "approved_with_guardrails"
    assert rows["mild_tier_handling"] == "blocked_from_execution"
    assert rows["replay_boundary"] == "still_blocked"
