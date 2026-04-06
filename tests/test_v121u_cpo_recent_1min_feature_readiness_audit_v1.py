from pathlib import Path

from a_share_quant.strategy.v121u_cpo_recent_1min_feature_readiness_audit_v1 import (
    V121UCpoRecent1MinFeatureReadinessAuditAnalyzer,
)


def test_v121u_recent_1min_feature_readiness_audit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121UCpoRecent1MinFeatureReadinessAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    assert result.summary["file_count"] >= 1
    assert result.summary["feature_family_count"] >= 1
