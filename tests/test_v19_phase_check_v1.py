from __future__ import annotations

from a_share_quant.strategy.v19_phase_check_v1 import V19PhaseCheckAnalyzer


def test_v19_phase_check_keeps_branch_bounded_after_rereview() -> None:
    result = V19PhaseCheckAnalyzer().analyze(
        phase_charter_payload={
            "summary": {"do_open_v19_now": True, "acceptance_posture": "open_v19_breadth_evidence_rereview"}
        },
        feature_breadth_rereview_payload={
            "summary": {
                "reviewed_feature_count": 2,
                "shortfall_changed_count": 1,
                "breadth_gap_materially_reduced_count": 1,
                "breadth_gap_partially_reduced_count": 1,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "keep_v19_active_but_bounded_as_breadth_evidence_rereview"
    assert result.summary["promote_retained_now"] is False
    assert result.summary["do_integrate_into_strategy_now"] is False
