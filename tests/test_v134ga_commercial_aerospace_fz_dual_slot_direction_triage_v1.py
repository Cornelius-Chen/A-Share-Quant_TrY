from pathlib import Path

from a_share_quant.strategy.v134ga_commercial_aerospace_fz_dual_slot_direction_triage_v1 import (
    V134GACommercialAerospaceFZDualSlotDirectionTriageV1Analyzer,
)


def test_v134ga_commercial_aerospace_fz_dual_slot_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GACommercialAerospaceFZDualSlotDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_dual_slot_permission_view_as_local_supervision_and_keep_single_ranker_blocked"
    )
