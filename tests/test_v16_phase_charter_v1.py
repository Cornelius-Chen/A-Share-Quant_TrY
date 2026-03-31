from __future__ import annotations

from a_share_quant.strategy.v16_phase_charter_v1 import V16PhaseCharterAnalyzer


def test_v16_phase_charter_opens_after_v15_waiting_state_with_provisional_candidates() -> None:
    result = V16PhaseCharterAnalyzer().analyze(
        v15_phase_closure_payload={"summary": {"enter_v15_waiting_state_now": True}},
        v15_feature_admissibility_review_payload={"summary": {"allow_provisional_candidacy_review_count": 4}},
    )

    assert result.summary["acceptance_posture"] == "open_v16_provisional_candidacy_stability_review"
    assert result.summary["do_open_v16_now"] is True
    assert result.summary["recommended_first_action"] == "freeze_v16_stability_review_protocol_v1"
