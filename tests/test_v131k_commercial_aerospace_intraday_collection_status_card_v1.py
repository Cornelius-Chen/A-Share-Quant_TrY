from pathlib import Path

from a_share_quant.strategy.v131k_commercial_aerospace_intraday_collection_status_card_v1 import (
    V131KCommercialAerospaceIntradayCollectionStatusCardAnalyzer,
)


def test_v131k_commercial_aerospace_intraday_collection_status_card_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131KCommercialAerospaceIntradayCollectionStatusCardAnalyzer(repo_root).analyze()

    assert result.summary["program_status"] == "blocked_for_minute_data"
    assert result.summary["required_artifact_count"] == 4
    assert result.summary["missing_artifact_count"] == 4
    assert "300342" in result.summary["highest_priority_missing_symbols"]
