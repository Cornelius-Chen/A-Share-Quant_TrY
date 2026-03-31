from __future__ import annotations

from a_share_quant.strategy.v16_phase_check_v1 import V16PhaseCheckAnalyzer


def test_v16_phase_check_keeps_branch_bounded_after_stability_review() -> None:
    result = V16PhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v16_now": True, "acceptance_posture": "open_v16_provisional_candidacy_stability_review", "recommended_first_action": "freeze_v16_stability_review_protocol_v1"}},
        feature_stability_review_payload={"summary": {"continue_provisional_candidacy_count": 4, "hold_for_more_stability_evidence_count": 0, "drop_from_provisional_candidacy_count": 0}},
    )

    assert result.summary["acceptance_posture"] == "keep_v16_active_but_bounded_as_stability_review"
    assert result.summary["v16_open"] is True
    assert result.summary["promote_retained_now"] is False
