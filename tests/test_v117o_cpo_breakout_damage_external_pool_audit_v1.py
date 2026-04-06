from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v117o_cpo_breakout_damage_external_pool_audit_v1 import (
    V117OCpoBreakoutDamageExternalPoolAuditAnalyzer,
)


def test_v117o_breakout_damage_external_pool_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117OCpoBreakoutDamageExternalPoolAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )

    assert result.summary["candidate_discriminator_name"] == "breakout_damage_containment_score_candidate"
    assert result.summary["add_row_count"] >= 10
    assert result.summary["positive_add_row_count"] >= 4
    assert result.summary["best_balanced_accuracy"] >= 0.5
    assert "external_pool_signal_clear" in result.summary
