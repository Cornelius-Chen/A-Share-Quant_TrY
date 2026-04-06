from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_v134hn_commercial_aerospace_hm_crowded_rebound_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python", "scripts/run_v134hn_commercial_aerospace_hm_crowded_rebound_direction_triage_v1.py"],
        cwd=repo_root,
        check=True,
    )
    report_path = (
        repo_root / "reports" / "analysis" / "v134hn_commercial_aerospace_hm_crowded_rebound_direction_triage_v1.json"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["crowding_like_shelter_rebound_count"] == 2
    directions = {row["symbol"]: row["direction"] for row in payload["triage_rows"]}
    assert directions["603601"] == "learn_as_crowded_shelter_rebound_not_board_restart"
    assert directions["002361"] == "learn_as_crowded_shelter_rebound_not_board_restart"
    assert directions["301306"] == "learn_as_high_beta_raw_only_rebound_without_unlock"
