from pathlib import Path

from a_share_quant.strategy.v134ct_commercial_aerospace_frontier_status_card_v1 import (
    V134CTCommercialAerospaceFrontierStatusCardV1Analyzer,
)


def test_v134ct_commercial_aerospace_frontier_status_card_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CTCommercialAerospaceFrontierStatusCardV1Analyzer(repo_root).analyze()

    assert result.summary["next_frontier"] == "intraday_add"
    assert result.summary["next_frontier_state"] == "deferred"
    assert any(row["key"] == "reduce_mainline_status" and row["value"] == "frozen" for row in result.status_rows)

