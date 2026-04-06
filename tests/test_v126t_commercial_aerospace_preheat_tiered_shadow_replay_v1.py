from pathlib import Path

from a_share_quant.strategy.v126t_commercial_aerospace_preheat_tiered_shadow_replay_v1 import (
    V126TCommercialAerospacePreheatTieredShadowReplayAnalyzer,
)


def test_v126t_preheat_tiered_shadow_replay_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126TCommercialAerospacePreheatTieredShadowReplayAnalyzer(repo_root).analyze()
    assert result.summary["final_equity"] > 0
