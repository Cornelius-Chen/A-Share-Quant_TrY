from pathlib import Path

from a_share_quant.strategy.v134ev_commercial_aerospace_broader_add_false_positive_audit_v1 import (
    V134EVCommercialAerospaceBroaderAddFalsePositiveAuditV1Analyzer,
)


def test_v134ev_commercial_aerospace_broader_add_false_positive_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134EVCommercialAerospaceBroaderAddFalsePositiveAuditV1Analyzer(repo_root).analyze()

    assert result.summary["seed_symbol_count"] == 12
    assert result.summary["total_session_count"] == 1224
    assert result.summary["seed_session_count"] == 55
    assert result.summary["non_seed_positive_hit_count"] == 495
    assert result.summary["non_seed_failed_hit_count"] == 2
    assert result.summary["non_seed_blocked_hit_count"] == 95
