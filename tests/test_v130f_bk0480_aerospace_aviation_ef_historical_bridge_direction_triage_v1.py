from pathlib import Path

from a_share_quant.strategy.v130f_bk0480_aerospace_aviation_ef_historical_bridge_direction_triage_v1 import (
    V130FBK0480AerospaceAviationEFHistoricalBridgeDirectionTriageAnalyzer,
)


def test_v130f_bk0480_aerospace_aviation_ef_historical_bridge_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130FBK0480AerospaceAviationEFHistoricalBridgeDirectionTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == (
        "freeze_bk0480_after_role_surface_v2_plus_historical_bridge_formalization_and_do_not_pretend_replay_readiness"
    )
    assert any(
        row["direction"] == "bk0480_replay_unlock" and row["status"] == "blocked"
        for row in result.direction_rows
    )
