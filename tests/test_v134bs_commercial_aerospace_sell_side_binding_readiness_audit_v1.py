from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134bs_commercial_aerospace_sell_side_binding_readiness_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134bs_commercial_aerospace_sell_side_binding_readiness_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134bs_commercial_aerospace_sell_side_binding_readiness_audit_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["ready_shadow_input_count"] == 2
    assert payload["summary"]["ready_shadow_reference_count"] == 1
    assert payload["summary"]["missing_binding_component_count"] == 2
