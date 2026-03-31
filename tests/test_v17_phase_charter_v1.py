from __future__ import annotations

from a_share_quant.strategy.v17_phase_charter_v1 import V17PhaseCharterAnalyzer


def test_v17_phase_charter_opens_after_v16_waiting_state_with_continuing_candidates() -> None:
    result = V17PhaseCharterAnalyzer().analyze(
        v16_phase_closure_payload={"summary": {"enter_v16_waiting_state_now": True}},
        v16_feature_stability_review_payload={"summary": {"continue_provisional_candidacy_count": 4}},
    )

    assert result.summary["acceptance_posture"] == "open_v17_promotion_evidence_generation"
    assert result.summary["do_open_v17_now"] is True
    assert result.summary["recommended_first_action"] == "freeze_v17_promotion_evidence_protocol_v1"
