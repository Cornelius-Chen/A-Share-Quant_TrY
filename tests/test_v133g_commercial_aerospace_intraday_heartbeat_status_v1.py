from pathlib import Path

from a_share_quant.strategy.v133g_commercial_aerospace_intraday_heartbeat_status_v1 import (
    V133GCommercialAerospaceIntradayHeartbeatStatusAnalyzer,
)


def test_v133g_intraday_heartbeat_status_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133GCommercialAerospaceIntradayHeartbeatStatusAnalyzer(repo_root).analyze()

    assert report.summary["program_status"] == "frozen"
    assert report.summary["missing_artifact_count"] == 3

