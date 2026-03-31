from __future__ import annotations

from a_share_quant.strategy.v17_phase_check_v1 import V17PhaseCheckAnalyzer


def test_v17_phase_check_keeps_branch_bounded_after_gap_review() -> None:
    result = V17PhaseCheckAnalyzer().analyze(
        phase_charter_payload={
            "summary": {
                "do_open_v17_now": True,
                "acceptance_posture": "open_v17_promotion_evidence_generation",
                "recommended_first_action": "freeze_v17_promotion_evidence_protocol_v1",
            }
        },
        feature_promotion_gap_review_payload={
            "summary": {
                "reviewed_feature_count": 4,
                "promotion_ready_now_count": 0,
                "needs_additional_promotion_evidence_count": 4,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "keep_v17_active_but_bounded_as_promotion_evidence_generation"
    assert result.summary["v17_open"] is True
    assert result.summary["promote_retained_now"] is False
