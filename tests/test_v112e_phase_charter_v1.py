from __future__ import annotations

from a_share_quant.strategy.v112e_phase_charter_v1 import V112EPhaseCharterAnalyzer


def test_v112e_phase_charter_opens_after_v112d_closure() -> None:
    result = V112EPhaseCharterAnalyzer().analyze(
        v112d_phase_closure_payload={"summary": {"v112d_success_criteria_met": True}}
    )

    assert result.summary["do_open_v112e_now"] is True
    assert result.summary["ready_for_attribution_review_next"] is True
