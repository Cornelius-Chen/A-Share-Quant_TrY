from pathlib import Path

from a_share_quant.strategy.v131j_commercial_aerospace_intraday_collection_change_gate_v1 import (
    V131JCommercialAerospaceIntradayCollectionChangeGateAnalyzer,
)


def test_v131j_commercial_aerospace_intraday_collection_change_gate_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131JCommercialAerospaceIntradayCollectionChangeGateAnalyzer(repo_root).analyze()

    assert result.summary["required_artifact_count"] == 4
    assert result.summary["present_artifact_count"] == 0
    assert result.summary["missing_artifact_count"] == 4
    assert any(row["symbol"] == "601698" for row in result.artifact_rows)
