from __future__ import annotations

from a_share_quant.strategy.v15_feature_candidacy_protocol_v1 import (
    V15FeatureCandidacyProtocolAnalyzer,
)


def test_v15_feature_candidacy_protocol_freezes_review_axes_and_candidates() -> None:
    result = V15FeatureCandidacyProtocolAnalyzer().analyze(
        v15_phase_charter_payload={"summary": {"do_open_v15_now": True}},
        v14_context_feature_schema_payload={
            "schema_rows": [
                {"feature_name": "single_pulse_support"},
                {"feature_name": "multi_day_reinforcement_support"},
            ]
        },
        v14_bounded_discrimination_payload={"summary": {"stable_discrimination_present": True}},
    )

    assert result.summary["acceptance_posture"] == "freeze_v15_feature_candidacy_protocol_v1"
    assert result.summary["candidate_feature_count"] == 2
    assert result.summary["review_axis_count"] == 4
    assert result.summary["ready_for_feature_admissibility_review_next"] is True
