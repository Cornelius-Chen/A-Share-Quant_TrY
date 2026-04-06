from pathlib import Path

from a_share_quant.strategy.v125f_commercial_aerospace_role_grammar_refresh_v3 import (
    V125FCommercialAerospaceRoleGrammarRefreshV3Analyzer,
)


def test_v125f_moves_000547_into_sentiment_watch() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125FCommercialAerospaceRoleGrammarRefreshV3Analyzer(repo_root).analyze()
    assert result.summary["000547_role_layer"] == "sentiment_watch"
