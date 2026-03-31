from __future__ import annotations

from a_share_quant.strategy.v16_stability_review_protocol_v1 import (
    V16StabilityReviewProtocolAnalyzer,
)


def test_v16_stability_review_protocol_freezes_provisional_candidates() -> None:
    result = V16StabilityReviewProtocolAnalyzer().analyze(
        v16_phase_charter_payload={"summary": {"do_open_v16_now": True}},
        v15_feature_admissibility_review_payload={
            "review_rows": [
                {"feature_name": "single_pulse_support", "candidacy_outcome": "allow_provisional_candidacy_review"},
                {"feature_name": "concept_indirectness_level", "candidacy_outcome": "hold_for_more_evidence"},
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "freeze_v16_stability_review_protocol_v1"
    assert result.summary["provisional_candidate_count"] == 1
    assert result.summary["review_axis_count"] == 4
    assert result.summary["ready_for_feature_stability_review_next"] is True
