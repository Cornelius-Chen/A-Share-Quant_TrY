from __future__ import annotations

from a_share_quant.strategy.v15_phase_check_v1 import V15PhaseCheckAnalyzer


def test_v15_phase_check_keeps_branch_bounded_after_admissibility_review() -> None:
    result = V15PhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v15_now": True, "acceptance_posture": "open_v15_retained_feature_candidacy_review", "recommended_first_action": "freeze_v15_feature_candidacy_protocol_v1"}},
        feature_admissibility_review_payload={"summary": {"allow_provisional_candidacy_review_count": 4, "hold_for_more_evidence_count": 1, "reject_candidacy_count": 0}},
    )

    assert result.summary["acceptance_posture"] == "keep_v15_active_but_bounded_as_candidacy_review"
    assert result.summary["v15_open"] is True
    assert result.summary["promote_retained_now"] is False
