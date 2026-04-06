from pathlib import Path

from a_share_quant.strategy.v126i_commercial_aerospace_two_layer_shadow_replay_v1 import (
    V126ICommercialAerospaceTwoLayerShadowReplayAnalyzer,
)


def test_v126i_two_layer_shadow_replay_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126ICommercialAerospaceTwoLayerShadowReplayAnalyzer(repo_root).analyze()
    assert result.summary["variant_count"] == 3
    assert len(result.variant_rows) == 3
    assert all(row["executed_order_count"] >= 0 for row in result.variant_rows)
