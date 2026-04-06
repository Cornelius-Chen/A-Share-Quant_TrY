from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134it_commercial_aerospace_is_outside_named_second_carrier_direction_triage_v1 import (
    V134ITCommercialAerospaceISOutsideNamedSecondCarrierDirectionTriageV1Analyzer,
)


def test_v134it_outside_named_second_carrier_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134ITCommercialAerospaceISOutsideNamedSecondCarrierDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["outside_named_watch_count"] == 1
    assert (
        result.summary["authoritative_status"]
        == "retain_000738_as_next_outside_named_second_carrier_watch_without_promoting_true_selection"
    )
    triage_by_role = {row["supervision_role"]: row for row in result.triage_rows}
    assert (
        triage_by_role["outside_named_local_leadership_second_carrier_watch"]["direction"]
        == "promote_as_next_event_backing_and_followthrough_extension_target"
    )
