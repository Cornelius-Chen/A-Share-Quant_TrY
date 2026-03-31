from __future__ import annotations

from a_share_quant.strategy.v15_phase_charter_v1 import V15PhaseCharterAnalyzer


def test_v15_phase_charter_opens_after_v14_waiting_state_and_positive_discrimination() -> None:
    result = V15PhaseCharterAnalyzer().analyze(
        v14_phase_closure_payload={"summary": {"enter_v14_waiting_state_now": True}},
        v14_context_feature_schema_payload={"summary": {"report_only_feature_count": 5}},
        v14_bounded_discrimination_payload={"summary": {"stable_discrimination_present": True}},
    )

    assert result.summary["acceptance_posture"] == "open_v15_retained_feature_candidacy_review"
    assert result.summary["do_open_v15_now"] is True
    assert result.summary["recommended_first_action"] == "freeze_v15_feature_candidacy_protocol_v1"
