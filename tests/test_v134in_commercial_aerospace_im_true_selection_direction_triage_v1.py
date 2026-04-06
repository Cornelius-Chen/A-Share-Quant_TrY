from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134in_commercial_aerospace_im_true_selection_direction_triage_v1 import (
    V134INCommercialAerospaceIMTrueSelectionDirectionTriageV1Analyzer,
)


def test_v134in_true_selection_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134INCommercialAerospaceIMTrueSelectionDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["remaining_hard_gap_count"] == 2
    assert (
        result.summary["authoritative_status"]
        == "retain_partial_gap_closure_but_keep_capital_true_selection_blocked"
    )
    triage_by_component = {row["component"]: row for row in result.triage_rows}
    assert "single-case" in triage_by_component["capital_true_selection"]["direction"]
    assert "supporting" in triage_by_component["board_event_alignment"]["direction"]
