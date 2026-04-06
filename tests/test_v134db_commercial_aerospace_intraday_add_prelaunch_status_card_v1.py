from pathlib import Path

from a_share_quant.strategy.v134db_commercial_aerospace_intraday_add_prelaunch_status_card_v1 import (
    V134DBCommercialAerospaceIntradayAddPrelaunchStatusCardV1Analyzer,
)


def test_v134db_commercial_aerospace_intraday_add_prelaunch_status_card_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134DBCommercialAerospaceIntradayAddPrelaunchStatusCardV1Analyzer(repo_root).analyze()

    assert result.summary["reduce_status"] == "frozen_mainline"
    assert result.summary["next_frontier"] == "intraday_add"
    assert result.summary["next_frontier_state"] == "deferred"
    assert any(row["key"] == "silent_opening_allowed" and row["value"] is False for row in result.status_rows)
