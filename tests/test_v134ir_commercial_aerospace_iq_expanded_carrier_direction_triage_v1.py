from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ir_commercial_aerospace_iq_expanded_carrier_direction_triage_v1 import (
    V134IRCommercialAerospaceIQExpandedCarrierDirectionTriageV1Analyzer,
)


def test_v134ir_expanded_carrier_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134IRCommercialAerospaceIQExpandedCarrierDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["priority_second_carrier_candidate_count"] == 1
    assert (
        result.summary["authoritative_status"]
        == "retain_one_priority_outside_named_search_candidate_without_promoting_true_selection"
    )
    triage_by_label = {row["carrier_search_label"]: row for row in result.triage_rows}
    assert (
        triage_by_label["priority_second_carrier_search_candidate"]["direction"]
        == "promote_as_next_outside_named_second_carrier_search_target"
    )
