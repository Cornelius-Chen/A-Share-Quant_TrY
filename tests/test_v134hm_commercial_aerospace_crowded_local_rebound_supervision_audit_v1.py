from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134hm_commercial_aerospace_crowded_local_rebound_supervision_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134hm_commercial_aerospace_crowded_local_rebound_supervision_audit_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134hm_commercial_aerospace_crowded_local_rebound_supervision_audit_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["analysis_symbol_count"] == 6
    assert payload["summary"]["crowding_like_shelter_rebound_count"] == 2
    by_symbol = {row["symbol"]: row for row in payload["symbol_rows"]}
    assert by_symbol["603601"]["crowded_rebound_family"] == "crowding_like_shelter_rebound"
    assert by_symbol["002361"]["crowded_rebound_family"] == "crowding_like_shelter_rebound"
    assert by_symbol["301306"]["crowded_rebound_family"] == "high_beta_raw_only_rebound"
    assert by_symbol["300342"]["crowded_rebound_family"] == "lockout_outlier_breakout"

