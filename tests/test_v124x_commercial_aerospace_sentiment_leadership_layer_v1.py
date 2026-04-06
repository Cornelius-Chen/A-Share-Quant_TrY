from pathlib import Path

from a_share_quant.strategy.v124x_commercial_aerospace_sentiment_leadership_layer_v1 import (
    V124XCommercialAerospaceSentimentLeadershipLayerAnalyzer,
)


def test_v124x_marks_at_least_one_sentiment_leader() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V124XCommercialAerospaceSentimentLeadershipLayerAnalyzer(repo_root).analyze()
    assert result.summary["sentiment_leader_count"] >= 1
