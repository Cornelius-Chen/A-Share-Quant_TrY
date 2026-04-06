from pathlib import Path

from a_share_quant.strategy.v134ge_commercial_aerospace_gd_dual_slot_capacity_direction_triage_v1 import (
    V134GECommercialAerospaceGDDualSlotCapacityDirectionTriageV1Analyzer,
)


def test_v134ge_commercial_aerospace_gd_dual_slot_capacity_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GECommercialAerospaceGDDualSlotCapacityDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_dual_slot_capacity_as_conditional_local_supervision_and_keep_add_execution_blocked"
    )
