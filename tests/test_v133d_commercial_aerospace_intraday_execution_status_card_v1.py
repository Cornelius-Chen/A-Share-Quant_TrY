from pathlib import Path

from a_share_quant.strategy.v133d_commercial_aerospace_intraday_execution_status_card_v1 import (
    V133DCommercialAerospaceIntradayExecutionStatusCardAnalyzer,
)


def test_v133d_intraday_execution_status_card_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133DCommercialAerospaceIntradayExecutionStatusCardAnalyzer(repo_root).analyze()

    assert report.summary["intraday_execution_status"] == "blocked"
    assert report.summary["blocked_component_count"] == 3

