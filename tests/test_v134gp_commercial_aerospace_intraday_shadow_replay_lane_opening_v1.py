from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gp_commercial_aerospace_intraday_shadow_replay_lane_opening_v1 import (
    V134GPCommercialAerospaceIntradayShadowReplayLaneOpeningV1Analyzer,
)


def test_v134gp_shadow_lane_opening() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GPCommercialAerospaceIntradayShadowReplayLaneOpeningV1Analyzer(repo_root).analyze()

    assert result.summary["frontier_name"] == "intraday_shadow_replay_lane"
    assert result.summary["frontier_state"] == "opened_protocol_only"
    assert result.summary["input_branch_count"] == 2
    assert result.summary["first_module"] == "reentry_unlock_shadow_bridge"
    assert result.summary["execution_authority"] == "still_blocked"

    rows = {row["opening_stage"]: row for row in result.opening_rows}
    assert rows["reduce_branch"]["status"] == "read_only_frozen_input"
    assert rows["add_branch"]["status"] == "read_only_frozen_supervision_input"
    assert rows["first_module"]["status"] == "reentry_unlock_bridge_first"

    report_path = repo_root / "reports" / "analysis" / "v134gp_commercial_aerospace_intraday_shadow_replay_lane_opening_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
