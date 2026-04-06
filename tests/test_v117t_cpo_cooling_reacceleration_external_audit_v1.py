from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v117s_cpo_cooling_reacceleration_discovery_v1 import (
    V117SCpoCoolingReaccelerationDiscoveryAnalyzer,
)
from a_share_quant.strategy.v117t_cpo_cooling_reacceleration_external_audit_v1 import (
    V117TCpoCoolingReaccelerationExternalAuditAnalyzer,
)


def test_v117t_cooling_reacceleration_external_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    upstream = V117SCpoCoolingReaccelerationDiscoveryAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    analyzer = V117TCpoCoolingReaccelerationExternalAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(v117s_payload=upstream.as_dict())

    assert result.summary["candidate_discriminator_name"] == "cooling_reacceleration_score_candidate"
    assert result.summary["best_balanced_accuracy"] >= 0.5
    assert "external_pool_signal_clear" in result.summary

