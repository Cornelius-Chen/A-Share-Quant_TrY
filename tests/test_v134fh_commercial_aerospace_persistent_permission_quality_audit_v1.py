from pathlib import Path

from a_share_quant.strategy.v134fh_commercial_aerospace_persistent_permission_quality_audit_v1 import (
    V134FHCommercialAerospacePersistentPermissionQualityAuditV1Analyzer,
)


def test_v134fh_commercial_aerospace_persistent_permission_quality_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FHCommercialAerospacePersistentPermissionQualityAuditV1Analyzer(repo_root).analyze()

    assert result.summary["persistent_session_count"] == 10
    assert result.summary["full_quality_count"] == 5
    assert result.summary["bridge_quality_count"] == 2
    assert result.summary["probe_quality_count"] == 3
