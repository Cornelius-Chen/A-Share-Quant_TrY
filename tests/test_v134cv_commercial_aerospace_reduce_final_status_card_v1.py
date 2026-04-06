from pathlib import Path

from a_share_quant.strategy.v134cv_commercial_aerospace_reduce_final_status_card_v1 import (
    V134CVCommercialAerospaceReduceFinalStatusCardV1Analyzer,
)


def test_v134cv_commercial_aerospace_reduce_final_status_card_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CVCommercialAerospaceReduceFinalStatusCardV1Analyzer(repo_root).analyze()

    assert result.summary["reduce_reopen_ready"] is False
    assert result.summary["next_frontier"] == "intraday_add"
    assert result.summary["next_frontier_state"] == "deferred"
    assert any(row["key"] == "reduce_status" and row["value"] == "frozen_mainline" for row in result.status_rows)

