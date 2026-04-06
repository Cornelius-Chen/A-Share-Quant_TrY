from pathlib import Path

from a_share_quant.strategy.v126q_commercial_aerospace_pruned_phase_geometry_shadow_replay_v1 import (
    V126QCommercialAerospacePrunedPhaseGeometryShadowReplayAnalyzer,
)


def test_v126q_pruned_phase_geometry_shadow_replay_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126QCommercialAerospacePrunedPhaseGeometryShadowReplayAnalyzer(repo_root).analyze()
    assert result.summary["executed_order_count"] >= 0
    assert result.summary["final_equity"] > 0
