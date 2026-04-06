from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v118l_cpo_breakout_damage_soft_component_external_audit_v1 import (
    V118LCpoBreakoutDamageSoftComponentExternalAuditAnalyzer,
)


def test_v118l_soft_component_external_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V118LCpoBreakoutDamageSoftComponentExternalAuditAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
        alpha=0.0,
    )
    assert result.summary["best_balanced_accuracy"] >= 0.772727

