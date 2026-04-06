from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v117w_cpo_cooling_reacceleration_false_positive_control_discovery_v1 import (
    V117WCpoCoolingReaccelerationFalsePositiveControlDiscoveryAnalyzer,
)
from a_share_quant.strategy.v117x_cpo_cooling_reacceleration_false_positive_control_external_audit_v1 import (
    V117XCpoCoolingReaccelerationFalsePositiveControlExternalAuditAnalyzer,
)


def test_v117x_cooling_reacceleration_false_positive_control_external_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    upstream = V117WCpoCoolingReaccelerationFalsePositiveControlDiscoveryAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    analyzer = V117XCpoCoolingReaccelerationFalsePositiveControlExternalAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(v117w_payload=upstream.as_dict())

    assert result.summary["candidate_name"] == "cooling_reacceleration_overheat_control_candidate"
    assert result.summary["best_balanced_accuracy"] >= 0.5

