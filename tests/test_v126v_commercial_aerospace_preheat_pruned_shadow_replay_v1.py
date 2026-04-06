from pathlib import Path

from a_share_quant.strategy.v126v_commercial_aerospace_preheat_pruned_shadow_replay_v1 import (
    V126VCommercialAerospacePreheatPrunedShadowReplayAnalyzer,
)


def test_v126v_preheat_pruned_shadow_replay_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126VCommercialAerospacePreheatPrunedShadowReplayAnalyzer(repo_root).analyze()
    assert result.summary["final_equity"] > 0
