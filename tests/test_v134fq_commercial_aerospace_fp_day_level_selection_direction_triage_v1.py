from pathlib import Path

from a_share_quant.strategy.v134fq_commercial_aerospace_fp_day_level_selection_direction_triage_v1 import (
    V134FQCommercialAerospaceFPDayLevelSelectionDirectionTriageV1Analyzer,
)


def test_v134fq_commercial_aerospace_fp_day_level_selection_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FQCommercialAerospaceFPDayLevelSelectionDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_add_local_hierarchy_but_shift_next_to_day_level_selection_authority_supervision"
    )
