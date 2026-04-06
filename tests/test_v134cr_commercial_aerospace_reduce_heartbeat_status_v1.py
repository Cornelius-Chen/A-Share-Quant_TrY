from pathlib import Path

from a_share_quant.strategy.v134cr_commercial_aerospace_reduce_heartbeat_status_v1 import (
    V134CRCommercialAerospaceReduceHeartbeatStatusV1Analyzer,
)


def test_v134cr_commercial_aerospace_reduce_heartbeat_status_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CRCommercialAerospaceReduceHeartbeatStatusV1Analyzer(repo_root).analyze()

    assert result.summary["reduce_status"] == "frozen_mainline"
    assert result.summary["execution_blocker_count"] == 4
    assert any(row["key"] == "next_frontier_state" and row["value"] == "intraday_add_deferred" for row in result.heartbeat_rows)

