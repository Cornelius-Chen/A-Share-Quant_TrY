from __future__ import annotations

from a_share_quant.strategy.v113g_phase_closure_check_v1 import V113GPhaseClosureCheckAnalyzer


def test_v113g_phase_closure_enters_waiting_state() -> None:
    result = V113GPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload={"summary": {"ready_for_phase_closure_next": True, "selected_archetype": "commercial_space_mainline", "validated_local_seed_count": 3, "owner_named_candidate_count": 10}},
    )

    assert result.summary["v113g_success_criteria_met"] is True
    assert result.summary["enter_v113g_waiting_state_now"] is True
