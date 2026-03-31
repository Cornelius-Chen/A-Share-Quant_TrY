from __future__ import annotations

from a_share_quant.strategy.v110a_probe_protocol_v1 import V110AProbeProtocolAnalyzer


def test_v110a_probe_protocol_freezes_zero_admit_safe_probe_rules() -> None:
    result = V110AProbeProtocolAnalyzer().analyze(
        v110a_phase_charter_payload={"summary": {"do_open_v110a_now": True}},
        v19_feature_breadth_rereview_payload={
            "review_rows": [
                {
                    "feature_name": "policy_followthrough_support",
                    "new_admitted_symbols": ["300750"],
                }
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "freeze_v110a_probe_protocol_v1"
    assert result.summary["allow_zero_admitted_as_successful_probe"] is True
    assert result.protocol["target_feature_name"] == "policy_followthrough_support"
