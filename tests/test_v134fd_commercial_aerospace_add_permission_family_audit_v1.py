from pathlib import Path

from a_share_quant.strategy.v134fd_commercial_aerospace_add_permission_family_audit_v1 import (
    V134FDCommercialAerospaceAddPermissionFamilyAuditV1Analyzer,
)


def test_v134fd_commercial_aerospace_add_permission_family_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FDCommercialAerospaceAddPermissionFamilyAuditV1Analyzer(repo_root).analyze()

    assert result.summary["high_confidence_session_count"] == 24
    assert result.summary["persistent_permission_candidate_count"] == 10
    assert result.summary["fragile_permission_watch_count"] == 7
    assert result.summary["failed_permission_watch_count"] == 7
