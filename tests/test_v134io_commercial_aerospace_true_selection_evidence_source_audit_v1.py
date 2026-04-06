from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134io_commercial_aerospace_true_selection_evidence_source_audit_v1 import (
    V134IOCommercialAerospaceTrueSelectionEvidenceSourceAuditV1Analyzer,
)


def test_v134io_true_selection_evidence_source_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134IOCommercialAerospaceTrueSelectionEvidenceSourceAuditV1Analyzer(repo_root).analyze()

    assert result.summary["remaining_hard_gap_count"] == 2
    assert result.summary["searched_symbol_count"] == 5
    assert result.summary["current_hard_counterpanel_count"] == 1
    assert result.summary["current_local_route_exhausted"] is True

    by_gap = {row["missing_gap"]: row for row in result.source_rows}
    assert by_gap["second_event_backed_carrier_case"]["next_evidence_source"] == "expanded_symbol_universe"
    assert by_gap["anchor_decoy_counterpanel"]["next_evidence_source"] == "attention_heat_evidence_expansion"
