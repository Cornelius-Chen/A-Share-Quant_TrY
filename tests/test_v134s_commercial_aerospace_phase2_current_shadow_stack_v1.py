from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134s_commercial_aerospace_phase2_current_shadow_stack_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for script_name in [
        "run_v134q_commercial_aerospace_broader_hit_mild_block_audit_v1.py",
        "run_v134s_commercial_aerospace_phase2_current_shadow_stack_v1.py",
    ]:
        subprocess.run([sys.executable, str(repo_root / "scripts" / script_name)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134s_commercial_aerospace_phase2_current_shadow_stack_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["current_phase2_wider_reference"] == "broader_hit_mild_blocked"
    assert report["summary"]["current_phase2_narrow_reference"] == "canonical_seed_simulator"
    statuses = {row["variant"]: row["status"] for row in report["stack_rows"]}
    assert statuses["broader_hit_mild_blocked"] == "current_phase2_wider_reference"
