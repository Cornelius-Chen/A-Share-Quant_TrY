from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134ao_commercial_aerospace_local_reversal_deferral_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    subprocess.run(
        ["python", "scripts/run_v134ao_commercial_aerospace_local_reversal_deferral_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )

    report_path = (
        repo_root / "reports" / "analysis" / "v134ao_commercial_aerospace_local_reversal_deferral_audit_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["summary"]["variant_count"] >= 3
    assert payload["summary"]["best_same_day_loss_avoided_delta_total"] >= 0
    assert payload["summary"]["best_rebound_cost_saved_5d_total"] >= 0
