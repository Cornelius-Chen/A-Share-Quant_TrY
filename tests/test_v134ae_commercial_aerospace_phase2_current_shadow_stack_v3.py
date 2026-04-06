from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134ae_commercial_aerospace_phase2_current_shadow_stack_v3() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    subprocess.run(
        ["python", "scripts/run_v134ae_commercial_aerospace_phase2_current_shadow_stack_v3.py"],
        cwd=repo_root,
        check=True,
    )

    report_path = (
        repo_root / "reports" / "analysis" / "v134ae_commercial_aerospace_phase2_current_shadow_stack_v3.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["current_phase2_wider_reference"] == "broader_hit_current_plus_reversal_100pct"
    assert report["summary"]["best_reversal_fraction"] == 1.0
    assert report["summary"]["phase2_best_same_day_loss_avoided_total"] == 45929.005

