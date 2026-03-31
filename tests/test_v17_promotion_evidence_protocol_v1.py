from __future__ import annotations

from a_share_quant.strategy.v17_promotion_evidence_protocol_v1 import (
    V17PromotionEvidenceProtocolAnalyzer,
)


def test_v17_promotion_evidence_protocol_freezes_continuing_candidates() -> None:
    result = V17PromotionEvidenceProtocolAnalyzer().analyze(
        v17_phase_charter_payload={"summary": {"do_open_v17_now": True}},
        v16_feature_stability_review_payload={
            "review_rows": [
                {"feature_name": "single_pulse_support", "stability_outcome": "continue_provisional_candidacy"},
                {"feature_name": "concept_confirmation_depth", "stability_outcome": "continue_provisional_candidacy"},
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "freeze_v17_promotion_evidence_protocol_v1"
    assert result.summary["provisional_candidate_count"] == 2
    assert result.summary["promotion_evidence_axis_count"] == 4
    assert result.summary["ready_for_per_feature_promotion_gap_review_next"] is True
