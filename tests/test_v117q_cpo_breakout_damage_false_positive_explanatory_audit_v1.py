from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117o_cpo_breakout_damage_external_pool_audit_v1 import (
    V117OCpoBreakoutDamageExternalPoolAuditAnalyzer,
)
from a_share_quant.strategy.v117q_cpo_breakout_damage_false_positive_explanatory_audit_v1 import (
    V117QCpoBreakoutDamageFalsePositiveExplanatoryAuditAnalyzer,
)


def test_v117q_breakout_damage_false_positive_explanatory_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    upstream = V117OCpoBreakoutDamageExternalPoolAuditAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    analyzer = V117QCpoBreakoutDamageFalsePositiveExplanatoryAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
        v117o_payload=upstream.as_dict(),
    )

    assert result.summary["passing_add_row_count"] >= result.summary["true_positive_pass_count"]
    assert len(result.explanatory_rows) == 4
    assert result.summary["top_explanatory_metric"] in {
        "reverse_candidate_score",
        "shooting_star_trap_score",
        "false_breakout_damage_proxy_score",
        "retail_chase_trap_score",
    }
