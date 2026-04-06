from pathlib import Path

from a_share_quant.strategy.v125q_commercial_aerospace_supervised_leakage_audit_v1 import (
    V125QCommercialAerospaceSupervisedLeakageAuditAnalyzer,
)


def test_v125q_has_no_feature_label_overlap() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125QCommercialAerospaceSupervisedLeakageAuditAnalyzer(repo_root).analyze()
    assert result.summary["potential_leakage_feature_count"] == 0
