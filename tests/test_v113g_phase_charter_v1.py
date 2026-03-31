from __future__ import annotations

from a_share_quant.strategy.v113g_phase_charter_v1 import V113GPhaseCharterAnalyzer


def test_v113g_phase_charter_opens_after_v113f_waiting_state() -> None:
    result = V113GPhaseCharterAnalyzer().analyze(
        v113f_phase_closure_payload={"summary": {"enter_v113f_waiting_state_now": True}},
        owner_continues_deep_study=True,
    )

    assert result.summary["do_open_v113g_now"] is True
    assert result.summary["selected_archetype"] == "commercial_space_mainline"
