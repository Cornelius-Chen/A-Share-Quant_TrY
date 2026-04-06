from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134ac_commercial_aerospace_reversal_sell_fraction_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    subprocess.run(
        ["python", "scripts/run_v134ac_commercial_aerospace_reversal_sell_fraction_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )

    report_path = (
        repo_root / "reports" / "analysis" / "v134ac_commercial_aerospace_reversal_sell_fraction_audit_v1.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["current_reversal_fraction"] == 0.5
    assert len(report["variant_rows"]) == 4
    fractions = {row["reversal_fraction"] for row in report["variant_rows"]}
    assert fractions == {0.25, 0.5, 0.75, 1.0}

