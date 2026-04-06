from pathlib import Path

from a_share_quant.strategy.v134gc_commercial_aerospace_gb_dual_slot_allocation_direction_triage_v1 import (
    V134GCCommercialAerospaceGBDualSlotAllocationDirectionTriageV1Analyzer,
)


def test_v134gc_commercial_aerospace_gb_dual_slot_allocation_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GCCommercialAerospaceGBDualSlotAllocationDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_dual_slot_allocation_as_local_supervision_and_keep_add_execution_blocked"
    )
