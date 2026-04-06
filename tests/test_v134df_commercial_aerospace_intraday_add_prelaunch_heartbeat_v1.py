from pathlib import Path

from a_share_quant.strategy.v134df_commercial_aerospace_intraday_add_prelaunch_heartbeat_v1 import (
    V134DFCommercialAerospaceIntradayAddPrelaunchHeartbeatV1Analyzer,
)


def test_v134df_commercial_aerospace_intraday_add_prelaunch_heartbeat_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134DFCommercialAerospaceIntradayAddPrelaunchHeartbeatV1Analyzer(repo_root).analyze()

    assert result.summary["frontier_name"] == "intraday_add"
    assert result.summary["frontier_state"] == "deferred"
    assert result.summary["silent_opening_allowed"] is False
    assert result.summary["ready_to_open_now"] is False
