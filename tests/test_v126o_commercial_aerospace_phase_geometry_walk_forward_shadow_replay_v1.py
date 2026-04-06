from pathlib import Path

from a_share_quant.strategy.v126o_commercial_aerospace_phase_geometry_walk_forward_shadow_replay_v1 import (
    V126OCommercialAerospacePhaseGeometryWalkForwardShadowReplayAnalyzer,
)


def test_v126o_phase_geometry_walk_forward_shadow_replay_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126OCommercialAerospacePhaseGeometryWalkForwardShadowReplayAnalyzer(repo_root).analyze()
    assert result.summary["executed_order_count"] >= 0
    assert result.summary["final_equity"] > 0
