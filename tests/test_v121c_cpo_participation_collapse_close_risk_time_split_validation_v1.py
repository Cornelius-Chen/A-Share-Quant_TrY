from pathlib import Path

from a_share_quant.strategy.v121a_cpo_participation_collapse_close_risk_discovery_v1 import (
    V121ACpoParticipationCollapseCloseRiskDiscoveryAnalyzer,
)
from a_share_quant.strategy.v121b_cpo_participation_collapse_close_risk_external_audit_v1 import (
    V121BCpoParticipationCollapseCloseRiskExternalAuditAnalyzer,
)
from a_share_quant.strategy.v121c_cpo_participation_collapse_close_risk_time_split_validation_v1 import (
    V121CCpoParticipationCollapseCloseRiskTimeSplitValidationAnalyzer,
)


def test_v121c_close_risk_time_split_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    discovery = V121ACpoParticipationCollapseCloseRiskDiscoveryAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    external = V121BCpoParticipationCollapseCloseRiskExternalAuditAnalyzer(repo_root=repo_root).analyze(
        v121a_payload=discovery.as_dict(),
    )
    analyzer = V121CCpoParticipationCollapseCloseRiskTimeSplitValidationAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(v121b_payload=external.as_dict())
    assert result.summary["split_count"] == 3
