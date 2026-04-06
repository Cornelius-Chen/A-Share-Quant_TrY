from pathlib import Path

from a_share_quant.strategy.v124y_commercial_aerospace_role_grammar_refresh_v2 import (
    V124YCommercialAerospaceRoleGrammarRefreshV2Analyzer,
)


def test_v124y_adds_sentiment_layer() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V124YCommercialAerospaceRoleGrammarRefreshV2Analyzer(repo_root).analyze()
    assert result.summary["sentiment_leadership_count"] >= 1
