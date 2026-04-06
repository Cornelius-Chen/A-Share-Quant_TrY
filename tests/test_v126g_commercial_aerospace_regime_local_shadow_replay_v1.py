from pathlib import Path

from a_share_quant.strategy.v126g_commercial_aerospace_regime_local_shadow_replay_v1 import (
    V126GCommercialAerospaceRegimeLocalShadowReplayAnalyzer,
)


def test_v126g_runs_regime_local_shadow_replay() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V126GCommercialAerospaceRegimeLocalShadowReplayAnalyzer(repo_root).analyze()
    assert result.summary["test_date_count"] > 0
