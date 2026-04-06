from pathlib import Path

from a_share_quant.strategy.v134gb_commercial_aerospace_dual_slot_allocation_supervision_audit_v1 import (
    V134GBCommercialAerospaceDualSlotAllocationSupervisionAuditV1Analyzer,
)


def test_v134gb_commercial_aerospace_dual_slot_allocation_supervision_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GBCommercialAerospaceDualSlotAllocationSupervisionAuditV1Analyzer(repo_root).analyze()

    assert result.summary["dual_slot_day_count"] == 1
    assert result.summary["allocation_row_count"] == 2
    assert result.summary["continuation_slot_weight"] == 0.033507
    assert result.summary["reset_slot_weight"] == 0.068632
    assert result.summary["reset_to_continuation_weight_ratio"] == 2.04828842
