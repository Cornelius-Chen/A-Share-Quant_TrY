from pathlib import Path

from a_share_quant.strategy.v134ez_commercial_aerospace_add_permission_context_audit_v1 import (
    V134EZCommercialAerospaceAddPermissionContextAuditV1Analyzer,
)


def test_v134ez_commercial_aerospace_add_permission_context_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134EZCommercialAerospaceAddPermissionContextAuditV1Analyzer(repo_root).analyze()

    assert result.summary["positive_hit_session_count"] == 542
    assert result.summary["best_slow_context_ratio"] == 5.4
    assert result.summary["best_point_in_time_broad_scenario"] == "contained_close15_plus_burst15_plus_posmin15"
    assert result.summary["best_point_in_time_broad_ratio"] == 4.93333333
    assert result.summary["best_high_confidence_scenario"] == "slow_unlock_high_role_plus_contained_burst15"
    assert result.summary["best_high_confidence_ratio"] == 3.8
