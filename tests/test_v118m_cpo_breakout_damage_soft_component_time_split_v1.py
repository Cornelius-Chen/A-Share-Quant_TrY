from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v118m_cpo_breakout_damage_soft_component_time_split_v1 import (
    V118MCpoBreakoutDamageSoftComponentTimeSplitAnalyzer,
)


def test_v118m_soft_component_time_split() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V118MCpoBreakoutDamageSoftComponentTimeSplitAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
        alpha=0.0,
    )
    assert result.summary["split_count"] == 3
