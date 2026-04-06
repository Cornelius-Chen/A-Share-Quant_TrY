from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v118k_cpo_breakout_damage_soft_component_integration_review_v1 import (
    V118KCpoBreakoutDamageSoftComponentIntegrationReviewAnalyzer,
)


def test_v118k_soft_component_integration_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V118KCpoBreakoutDamageSoftComponentIntegrationReviewAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    assert result.summary["base_best_balanced_accuracy"] == 0.772727
    assert len(result.alpha_rows) == 4

