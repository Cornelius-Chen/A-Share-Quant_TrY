from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134im_commercial_aerospace_capital_true_selection_readiness_audit_v1 import (
    V134IMCommercialAerospaceCapitalTrueSelectionReadinessAuditV1Analyzer,
)


def test_v134im_capital_true_selection_readiness_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134IMCommercialAerospaceCapitalTrueSelectionReadinessAuditV1Analyzer(repo_root).analyze()

    assert result.summary["named_gap_total"] == 4
    assert result.summary["explicitly_closed_gap_count"] == 2
    assert result.summary["remaining_hard_gap_count"] == 2
    assert result.summary["capital_true_selection_ready"] is False

    by_gap = {row["gap_name"]: row for row in result.gap_rows}
    assert by_gap["second_event_backed_carrier_case"]["current_status"] == "still_missing"
    assert by_gap["anchor_decoy_counterpanel"]["current_status"] == "still_thin"
    assert by_gap["symbol_followthrough_surface"]["current_status"] == "explicit_layer_now_present"
    assert by_gap["board_event_alignment"]["current_status"] == "explicit_layer_now_present"
