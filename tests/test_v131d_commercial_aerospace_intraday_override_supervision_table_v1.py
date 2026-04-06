from pathlib import Path

from a_share_quant.strategy.v131d_commercial_aerospace_intraday_override_supervision_table_v1 import (
    V131DCommercialAerospaceIntradayOverrideSupervisionTableAnalyzer,
)


def test_v131d_commercial_aerospace_intraday_override_supervision_table_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131DCommercialAerospaceIntradayOverrideSupervisionTableAnalyzer(repo_root).analyze()

    assert result.summary["buy_execution_row_count"] == 55
    assert result.summary["override_positive_count"] == 2
    assert result.summary["reversal_watch_count"] == 2
    assert result.summary["clean_control_count"] >= 20
    assert any(row["supervision_label"] == "override_positive" for row in result.supervision_rows)
