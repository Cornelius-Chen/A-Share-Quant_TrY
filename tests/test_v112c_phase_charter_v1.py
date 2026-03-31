from __future__ import annotations

from a_share_quant.strategy.v112c_phase_charter_v1 import V112CPhaseCharterAnalyzer


def test_v112c_phase_charter_opens_after_v112b_closure() -> None:
    result = V112CPhaseCharterAnalyzer().analyze(
        v112b_phase_closure_payload={"summary": {"v112b_success_criteria_met": True}}
    )

    assert result.summary["do_open_v112c_now"] is True
    assert result.summary["ready_for_hotspot_review_next"] is True
