from pathlib import Path

from a_share_quant.strategy.v123m_cpo_daily_residual_downside_discovery_v1 import (
    V123MCpoDailyResidualDownsideDiscoveryAnalyzer,
)
from a_share_quant.strategy.v123o_cpo_daily_residual_downside_boundary_false_positive_audit_v1 import (
    V123OCpoDailyResidualDownsideBoundaryFalsePositiveAuditAnalyzer,
)


def test_v123o_daily_residual_downside_boundary_audit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    discovery = V123MCpoDailyResidualDownsideDiscoveryAnalyzer(repo_root=repo_root).analyze()
    result = V123OCpoDailyResidualDownsideBoundaryFalsePositiveAuditAnalyzer(repo_root=repo_root).analyze(
        v123m_payload=discovery.as_dict()
    )
    assert result.summary["positive_pass_rate"] > result.summary["pre_interval_false_positive_rate"]
    assert result.summary["positive_pass_rate"] > result.summary["post_interval_false_positive_rate"]
