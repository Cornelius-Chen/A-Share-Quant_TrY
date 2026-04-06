from pathlib import Path

from a_share_quant.strategy.v134cp_commercial_aerospace_reduce_to_intraday_add_transition_protocol_v1 import (
    V134CPCommercialAerospaceReduceToIntradayAddTransitionProtocolV1Analyzer,
)


def test_v134cp_commercial_aerospace_reduce_to_intraday_add_transition_protocol_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CPCommercialAerospaceReduceToIntradayAddTransitionProtocolV1Analyzer(repo_root).analyze()

    assert result.summary["intraday_add_frontier_status"] == "approved_but_not_opened_in_this_step"
    assert "future_handoff" not in result.summary  # keep summary narrow
    assert any(row["transition_stage"] == "freeze_reduce_mainline" for row in result.protocol_rows)

