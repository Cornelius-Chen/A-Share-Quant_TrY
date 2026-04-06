from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134ap_commercial_aerospace_ao_local_deferral_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    subprocess.run(
        ["python", "scripts/run_v134ao_commercial_aerospace_local_reversal_deferral_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["python", "scripts/run_v134ap_commercial_aerospace_ao_local_deferral_direction_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )

    report_path = (
        repo_root / "reports" / "analysis" / "v134ap_commercial_aerospace_ao_local_deferral_direction_triage_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["authoritative_status"] in {
        "promote_local_reversal_deferral_inside_phase2_wider_reference",
        "retain_local_reversal_deferral_as_supervision_only",
    }
