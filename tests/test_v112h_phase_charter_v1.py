from __future__ import annotations

from a_share_quant.strategy.v112h_phase_charter_v1 import V112HPhaseCharterAnalyzer


def test_v112h_phase_charter_opens_review_only_candidate_draft() -> None:
    analyzer = V112HPhaseCharterAnalyzer()
    result = analyzer.analyze(phase_check_payload={"summary": {"enter_v112g_waiting_state_now": True}})

    assert result.summary["ready_for_candidate_substate_draft_next"] is True
    assert result.charter["mission"].startswith("Generate a review-only candidate substate draft")
