from pathlib import Path

from a_share_quant.strategy.v133c_commercial_aerospace_intraday_execution_unblock_protocol_v1 import (
    V133CCommercialAerospaceIntradayExecutionUnblockProtocolAnalyzer,
)


def test_v133c_intraday_execution_unblock_protocol_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133CCommercialAerospaceIntradayExecutionUnblockProtocolAnalyzer(repo_root).analyze()

    assert report.summary["blocked_requirement_count"] == 3
    assert report.summary["ready_requirement_count"] == 1

