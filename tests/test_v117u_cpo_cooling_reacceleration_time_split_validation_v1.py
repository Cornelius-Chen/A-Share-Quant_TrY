from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v117s_cpo_cooling_reacceleration_discovery_v1 import (
    V117SCpoCoolingReaccelerationDiscoveryAnalyzer,
)
from a_share_quant.strategy.v117t_cpo_cooling_reacceleration_external_audit_v1 import (
    V117TCpoCoolingReaccelerationExternalAuditAnalyzer,
)
from a_share_quant.strategy.v117u_cpo_cooling_reacceleration_time_split_validation_v1 import (
    V117UCpoCoolingReaccelerationTimeSplitValidationAnalyzer,
)


def test_v117u_cooling_reacceleration_time_split_validation() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    discovery = V117SCpoCoolingReaccelerationDiscoveryAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    external = V117TCpoCoolingReaccelerationExternalAuditAnalyzer(repo_root=repo_root).analyze(
        v117s_payload=discovery.as_dict(),
    )
    analyzer = V117UCpoCoolingReaccelerationTimeSplitValidationAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(v117t_payload=external.as_dict())

    assert result.summary["split_count"] == 3
    assert 0.0 <= result.summary["mean_test_balanced_accuracy"] <= 1.0
