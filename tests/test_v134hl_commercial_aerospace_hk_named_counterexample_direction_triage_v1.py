from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134hl_commercial_aerospace_hk_named_counterexample_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134hl_commercial_aerospace_hk_named_counterexample_direction_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134hl_commercial_aerospace_hk_named_counterexample_direction_triage_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["analysis_symbol_count"] == 6
    assert payload["summary"]["crossed_pre_lockout_peak_count"] == 2
    directions = {row["symbol"]: row["direction"] for row in payload["triage_rows"]}
    assert directions["300342"] == "learn_as_board_locked_outlier_breakout_not_board_restart"
    assert directions["603601"] == "learn_as_post_lockout_raw_breakout_without_unlock_authority"
    assert directions["002361"] == "learn_as_weak_repair_inside_locked_board"
