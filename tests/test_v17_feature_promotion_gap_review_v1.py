from __future__ import annotations

from a_share_quant.strategy.v17_feature_promotion_gap_review_v1 import (
    V17FeaturePromotionGapReviewAnalyzer,
)


def test_v17_feature_promotion_gap_review_states_shortfalls_without_promotion() -> None:
    result = V17FeaturePromotionGapReviewAnalyzer().analyze(
        promotion_evidence_protocol_payload={
            "summary": {"ready_for_per_feature_promotion_gap_review_next": True},
            "protocol": {"provisional_candidate_feature_names": ["single_pulse_support"]},
        },
        feature_stability_review_payload={
            "review_rows": [
                {"feature_name": "single_pulse_support", "stability_outcome": "continue_provisional_candidacy"}
            ]
        },
        feature_admissibility_review_payload={
            "review_rows": [
                {"feature_name": "single_pulse_support", "admissible_for_candidacy_review": True}
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "open_v17_feature_promotion_gap_review_v1_as_bounded_review"
    assert result.summary["reviewed_feature_count"] == 1
    assert result.summary["promotion_ready_now_count"] == 0
    assert result.summary["needs_additional_promotion_evidence_count"] == 1
