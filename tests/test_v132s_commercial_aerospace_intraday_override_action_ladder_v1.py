from pathlib import Path

from a_share_quant.strategy.v132s_commercial_aerospace_intraday_override_action_ladder_v1 import (
    V132SCommercialAerospaceIntradayOverrideActionLadderAnalyzer,
)


def test_v132s_intraday_override_action_ladder_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V132SCommercialAerospaceIntradayOverrideActionLadderAnalyzer(repo_root).analyze()

    assert report.summary["tier_count"] == 3
    assert report.action_rows[0]["governance_action"] == "emergency_exit_shadow_override"

