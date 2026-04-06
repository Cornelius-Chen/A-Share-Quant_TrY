from pathlib import Path

from a_share_quant.strategy.v123e_cpo_1min_downside_same_plane_integration_audit_v1 import (
    V123ECpo1MinDownsideSamePlaneIntegrationAuditAnalyzer,
)


def test_v123e_same_plane_integration_has_no_material_increment() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V123ECpo1MinDownsideSamePlaneIntegrationAuditAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["variant_count"] == 6
    assert result.summary["material_increment_over_downside_failure"] is False

