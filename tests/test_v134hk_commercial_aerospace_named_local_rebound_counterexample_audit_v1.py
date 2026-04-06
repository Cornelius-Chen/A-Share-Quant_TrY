from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134hk_commercial_aerospace_named_local_rebound_counterexample_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134hk_commercial_aerospace_named_local_rebound_counterexample_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134hk_commercial_aerospace_named_local_rebound_counterexample_audit_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["analysis_symbol_count"] == 6
    assert payload["summary"]["crossed_pre_lockout_peak_count"] == 2
    by_symbol = {row["symbol"]: row for row in payload["symbol_rows"]}
    assert by_symbol["300342"]["counterexample_family"] == "lockout_outlier_breakout_then_fade"
    assert by_symbol["603601"]["counterexample_family"] == "raw_only_post_lockout_breakout_without_board_context"
    assert by_symbol["301306"]["counterexample_family"] == "raw_only_near_high_rebound_without_breakout"
    assert by_symbol["600343"]["counterexample_family"] == "coverage_gap_or_inactive"

