from pathlib import Path

from a_share_quant.strategy.v134gd_commercial_aerospace_dual_slot_capacity_audit_v1 import (
    V134GDCommercialAerospaceDualSlotCapacityAuditV1Analyzer,
)


def test_v134gd_commercial_aerospace_dual_slot_capacity_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GDCommercialAerospaceDualSlotCapacityAuditV1Analyzer(repo_root).analyze()

    assert result.summary["active_wave_day_count"] == 2
    assert result.summary["dual_slot_day_count"] == 1
    assert result.summary["single_slot_day_count"] == 0
    assert result.summary["zero_slot_day_count"] == 1
