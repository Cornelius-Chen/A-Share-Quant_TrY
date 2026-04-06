import json
from pathlib import Path

from a_share_quant.strategy.v123m_cpo_daily_residual_downside_discovery_v1 import (
    V123MCpoDailyResidualDownsideDiscoveryAnalyzer,
)
from a_share_quant.strategy.v123n_cpo_daily_residual_downside_time_split_audit_v1 import (
    V123NCpoDailyResidualDownsideTimeSplitAuditAnalyzer,
)


def test_v123n_daily_residual_downside_time_split_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    discovery = V123MCpoDailyResidualDownsideDiscoveryAnalyzer(repo_root=repo_root).analyze()
    payload = discovery.as_dict()
    result = V123NCpoDailyResidualDownsideTimeSplitAuditAnalyzer(repo_root=repo_root).analyze(v123m_payload=payload)
    assert result.summary["split_count"] >= 2
    assert result.summary["mean_test_balanced_accuracy"] > 0.5
