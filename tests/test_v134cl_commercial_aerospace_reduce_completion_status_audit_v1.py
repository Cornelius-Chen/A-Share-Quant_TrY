from pathlib import Path

from a_share_quant.strategy.v134cl_commercial_aerospace_reduce_completion_status_audit_v1 import (
    V134CLCommercialAerospaceReduceCompletionStatusAuditV1Analyzer,
)


def test_v134cl_commercial_aerospace_reduce_completion_status_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CLCommercialAerospaceReduceCompletionStatusAuditV1Analyzer(repo_root).analyze()

    assert result.summary["governance_stack_ready"] is True
    assert result.summary["sell_side_binding_reference_ready"] is True
    assert result.summary["broad_reduce_tuning_stopped"] is True
    assert result.summary["local_residue_supervision_only"] is True
    assert result.summary["full_execution_binding_still_blocked"] is True
    assert result.summary["remaining_execution_blocker_count"] == 4
    assert result.summary["residue_seed_count"] == 4

