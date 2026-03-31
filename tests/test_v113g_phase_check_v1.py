from __future__ import annotations

from a_share_quant.strategy.v113g_phase_check_v1 import V113GPhaseCheckAnalyzer


def test_v113g_phase_check_keeps_scope_freeze_posture() -> None:
    result = V113GPhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v113g_now": True, "selected_archetype": "commercial_space_mainline"}},
        study_scope_payload={"summary": {"validated_local_seed_count": 3, "owner_named_candidate_count": 10, "bounded_study_dimension_count": 8}},
    )

    assert result.summary["ready_for_phase_closure_next"] is True
    assert result.summary["allow_auto_training_now"] is False
