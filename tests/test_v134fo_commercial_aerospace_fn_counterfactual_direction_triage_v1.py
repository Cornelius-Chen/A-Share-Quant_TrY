from pathlib import Path

from a_share_quant.strategy.v134fo_commercial_aerospace_fn_counterfactual_direction_triage_v1 import (
    V134FOCommercialAerospaceFNCounterfactualDirectionTriageV1Analyzer,
)


def test_v134fo_commercial_aerospace_fn_counterfactual_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FOCommercialAerospaceFNCounterfactualDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "keep_add_portability_blocked_and_shift_next_to_day_level_selection_authority_supervision"
    )
