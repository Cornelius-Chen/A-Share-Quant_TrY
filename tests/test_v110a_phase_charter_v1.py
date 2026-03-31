from __future__ import annotations

from a_share_quant.strategy.v110a_phase_charter_v1 import V110APhaseCharterAnalyzer


def test_v110a_phase_charter_opens_single_owner_led_probe() -> None:
    result = V110APhaseCharterAnalyzer().analyze(
        v19_phase_closure_payload={"summary": {"enter_v19_waiting_state_now": True}},
        v19_feature_breadth_rereview_payload={
            "review_rows": [
                {
                    "feature_name": "policy_followthrough_support",
                    "updated_primary_shortfall": "sample_breadth_gap",
                }
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "open_v110a_policy_followthrough_cross_family_breadth_probe"
    assert result.summary["do_open_v110a_now"] is True
    assert result.charter["allow_auto_follow_on_phase"] is False
