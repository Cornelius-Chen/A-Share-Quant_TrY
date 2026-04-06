from pathlib import Path

from a_share_quant.strategy.v134id_commercial_aerospace_ic_carrier_gap_direction_triage_v1 import (
    V134IDCommercialAerospaceICCarrierGapDirectionTriageV1Analyzer,
)


def test_v134id_carrier_gap_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134IDCommercialAerospaceICCarrierGapDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["active_gap_count"] == 4
    directions = {row["next_target"]: row["direction"] for row in report.triage_rows}
    assert directions["second_event_backed_carrier_case"] == "promote_as_next_high_value_search_target"
    assert directions["capital_true_selection"] == "keep_blocked_until_the_named_gaps_are_partially_closed"
