from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134aq_commercial_aerospace_phase2_current_shadow_stack_v4() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    subprocess.run(
        ["python", "scripts/run_v134ao_commercial_aerospace_local_reversal_deferral_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134aq_commercial_aerospace_phase2_current_shadow_stack_v4.py"],
        cwd=repo_root,
        check=True,
    )

    report_path = repo_root / "reports" / "analysis" / "v134aq_commercial_aerospace_phase2_current_shadow_stack_v4.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["phase2_best_same_day_loss_avoided_total"] >= 45929.005
