from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gp_commercial_aerospace_intraday_shadow_replay_lane_opening_v1 import (
    V134GPCommercialAerospaceIntradayShadowReplayLaneOpeningV1Analyzer,
)
from a_share_quant.strategy.v134gq_commercial_aerospace_gp_shadow_lane_direction_triage_v1 import (
    V134GQCommercialAerospaceGPShadowLaneDirectionTriageV1Analyzer,
)


def test_v134gq_shadow_lane_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    opening = V134GPCommercialAerospaceIntradayShadowReplayLaneOpeningV1Analyzer(repo_root).analyze()
    opening_path = repo_root / "reports" / "analysis" / "v134gp_commercial_aerospace_intraday_shadow_replay_lane_opening_v1.json"
    opening_path.write_text(json.dumps(opening.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134GQCommercialAerospaceGPShadowLaneDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["frontier_state"] == "opened_protocol_only"
    assert result.summary["first_module"] == "reentry_unlock_shadow_bridge"
    assert result.summary["execution_authority"] == "still_blocked"

    rows = {row["component"]: row for row in result.triage_rows}
    assert rows["intraday_shadow_replay_lane"]["status"] == "opened_as_protocol_only"
    assert rows["first_module"]["status"] == "reentry_unlock_shadow_bridge"
    assert rows["execution_authority"]["status"] == "still_blocked"

    report_path = repo_root / "reports" / "analysis" / "v134gq_commercial_aerospace_gp_shadow_lane_direction_triage_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
