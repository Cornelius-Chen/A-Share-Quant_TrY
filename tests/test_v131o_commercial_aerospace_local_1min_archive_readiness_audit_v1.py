from pathlib import Path

from a_share_quant.strategy.v131o_commercial_aerospace_local_1min_archive_readiness_audit_v1 import (
    V131OCommercialAerospaceLocal1MinArchiveReadinessAuditAnalyzer,
)


def test_v131o_commercial_aerospace_local_1min_archive_readiness_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131OCommercialAerospaceLocal1MinArchiveReadinessAuditAnalyzer(repo_root).analyze()
    assert result.summary["manifest_row_count"] >= 4
    assert result.summary["ready_count"] == result.summary["manifest_row_count"]
    assert result.summary["local_1min_fully_ready"] is True
