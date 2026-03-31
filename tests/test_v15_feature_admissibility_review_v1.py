from __future__ import annotations

from a_share_quant.strategy.v15_feature_admissibility_review_v1 import (
    V15FeatureAdmissibilityReviewAnalyzer,
)


def test_v15_feature_admissibility_review_marks_indirectness_as_hold() -> None:
    result = V15FeatureAdmissibilityReviewAnalyzer().analyze(
        candidacy_protocol_payload={
            "summary": {"ready_for_feature_admissibility_review_next": True},
            "protocol": {"candidate_feature_names": ["single_pulse_support", "concept_indirectness_level"]},
        },
        context_feature_schema_payload={
            "schema_rows": [
                {"feature_name": "single_pulse_support", "report_only": True},
                {"feature_name": "concept_indirectness_level", "report_only": True},
            ]
        },
        bounded_discrimination_payload={"summary": {"stable_discrimination_present": True}, "discrimination_rows": []},
    )

    assert result.summary["acceptance_posture"] == "open_v15_feature_admissibility_review_v1_as_bounded_review"
    assert result.summary["reviewed_feature_count"] == 2
    assert result.summary["allow_provisional_candidacy_review_count"] == 1
    assert result.summary["hold_for_more_evidence_count"] == 1
