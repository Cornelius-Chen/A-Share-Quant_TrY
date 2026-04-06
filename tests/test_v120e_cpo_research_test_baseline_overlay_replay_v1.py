from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v120e_cpo_research_test_baseline_overlay_replay_v1 import (
    CpoResearchTestBaselineOverlayReplayAnalyzer,
)


def test_research_test_baseline_overlay_replay_runs_and_keeps_overlay_bounded() -> None:
    result = CpoResearchTestBaselineOverlayReplayAnalyzer().analyze()
    assert result.summary["research_overlay_order_count"] > 0
    assert result.summary["research_test_final_equity"] >= result.summary["baseline_final_equity"]
    assert "breakout_damage_soft_component" in result.summary["excluded_non_dead_component_names"]
    assert any("held_position_only" in row["overlay_scope"] for row in result.executed_overlay_rows)
