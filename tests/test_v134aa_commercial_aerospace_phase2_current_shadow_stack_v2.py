from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134aa_commercial_aerospace_phase2_current_shadow_stack_v2() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    subprocess.run(
        ["python", "scripts/run_v134aa_commercial_aerospace_phase2_current_shadow_stack_v2.py"],
        cwd=repo_root,
        check=True,
    )

    report_path = repo_root / "reports" / "analysis" / "v134aa_commercial_aerospace_phase2_current_shadow_stack_v2.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert (
        report["summary"]["current_phase2_wider_reference"]
        == "broader_hit_mild_blocked_plus_reversal_late_severe_block"
    )
    assert report["summary"]["phase2_best_same_day_loss_avoided_total"] == 26915.5372
    statuses = {row["variant"]: row["status"] for row in report["stack_rows"]}
    assert statuses["broader_hit_mild_blocked_plus_reversal_late_severe_block"] == "current_phase2_wider_reference"
