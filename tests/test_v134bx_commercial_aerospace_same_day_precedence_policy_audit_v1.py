from pathlib import Path

from a_share_quant.strategy.v134bx_commercial_aerospace_same_day_precedence_policy_audit_v1 import (
    V134BXCommercialAerospaceSameDayPrecedencePolicyAuditV1Analyzer,
)


def test_v134bx_commercial_aerospace_same_day_precedence_policy_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134BXCommercialAerospaceSameDayPrecedencePolicyAuditV1Analyzer(repo_root).analyze()

    assert result.summary["collision_session_count"] == 8
    assert result.summary["collision_family_count"] == 5
    assert result.summary["open_or_add_collision_count"] == 6
    assert result.summary["reduce_or_close_collision_count"] == 4
    assert result.summary["largest_collision_family"] == "add"
    assert any(
        row["policy_name"] == "open_add_protection" and row["status"] == "mandatory"
        for row in result.policy_rows
    )
