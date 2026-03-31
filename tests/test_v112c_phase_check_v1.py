from __future__ import annotations

from a_share_quant.strategy.v112c_phase_check_v1 import V112CPhaseCheckAnalyzer


def test_v112c_phase_check_stays_report_only() -> None:
    result = V112CPhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112c_now": True}},
        hotspot_review_payload={"summary": {"primary_reading": "x", "ready_for_sidecar_protocol_next": True}},
        sidecar_protocol_payload={"summary": {"candidate_model_family_count": 2, "ready_for_phase_check_next": True}},
    )

    assert result.summary["hotspot_review_present"] is True
    assert result.summary["sidecar_protocol_present"] is True
    assert result.summary["allow_sidecar_deployment_now"] is False
