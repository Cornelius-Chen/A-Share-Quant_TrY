from __future__ import annotations

from a_share_quant.strategy.v16_feature_stability_review_v1 import (
    V16FeatureStabilityReviewAnalyzer,
)


def test_v16_feature_stability_review_keeps_provisional_candidates_alive() -> None:
    result = V16FeatureStabilityReviewAnalyzer().analyze(
        stability_protocol_payload={
            "summary": {"ready_for_feature_stability_review_next": True},
            "protocol": {"provisional_candidate_feature_names": ["single_pulse_support"]},
        },
        feature_admissibility_review_payload={
            "review_rows": [
                {
                    "feature_name": "single_pulse_support",
                    "admissible_for_candidacy_review": True,
                    "point_in_time_clean_definition": True,
                    "binding_rule_stable_and_auditable": True,
                    "safe_containment": True,
                }
            ]
        },
        bounded_discrimination_payload={"summary": {"stable_discrimination_present": True}},
    )

    assert result.summary["acceptance_posture"] == "open_v16_feature_stability_review_v1_as_bounded_review"
    assert result.summary["reviewed_feature_count"] == 1
    assert result.summary["continue_provisional_candidacy_count"] == 1
