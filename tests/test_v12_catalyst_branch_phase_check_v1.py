from __future__ import annotations

from a_share_quant.strategy.v12_catalyst_branch_phase_check_v1 import (
    V12CatalystBranchPhaseCheckAnalyzer,
)


def test_v12_catalyst_branch_phase_check_keeps_branch_bounded() -> None:
    catalyst_audit_payload = {
        "summary": {
            "context_separation_present": True,
            "keep_branch_report_only": True,
        }
    }
    bottleneck_check_payload = {
        "summary": {
            "acceptance_posture": "keep_v12_primary_bottleneck_as_carry_row_diversity_gap"
        }
    }

    result = V12CatalystBranchPhaseCheckAnalyzer().analyze(
        catalyst_audit_payload=catalyst_audit_payload,
        bottleneck_check_payload=bottleneck_check_payload,
    )

    assert result.summary["context_separation_present"] is True
    assert result.summary["primary_bottleneck_still_carry_row_diversity"] is True
    assert result.summary["catalyst_branch_changes_v12_direction_now"] is False
    assert result.summary["promote_catalyst_branch_now"] is False
