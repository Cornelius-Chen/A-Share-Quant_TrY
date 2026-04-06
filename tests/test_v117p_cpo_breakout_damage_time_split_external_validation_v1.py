from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117o_cpo_breakout_damage_external_pool_audit_v1 import (
    V117OCpoBreakoutDamageExternalPoolAuditAnalyzer,
)
from a_share_quant.strategy.v117p_cpo_breakout_damage_time_split_external_validation_v1 import (
    V117PCpoBreakoutDamageTimeSplitExternalValidationAnalyzer,
)


def test_v117p_breakout_damage_time_split_external_validation() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    upstream = V117OCpoBreakoutDamageExternalPoolAuditAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    analyzer = V117PCpoBreakoutDamageTimeSplitExternalValidationAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117o_payload=upstream.as_dict(),
    )

    assert result.summary["split_count"] == 3
    assert 0.0 <= result.summary["mean_test_balanced_accuracy"] <= 1.0
    assert len(result.split_rows) == 3
