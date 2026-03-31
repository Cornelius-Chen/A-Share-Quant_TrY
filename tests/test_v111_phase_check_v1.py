from __future__ import annotations

from a_share_quant.strategy.v111_phase_check_v1 import V111PhaseCheckAnalyzer


def test_v111_phase_check_keeps_branch_exploration_only() -> None:
    result = V111PhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v111_now": True}},
        infrastructure_plan_payload={
            "summary": {
                "acquisition_scope_count": 4,
                "source_hierarchy_count": 4,
                "ready_for_bounded_first_pilot_next": True,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "keep_v111_active_but_exploration_layer_only"
    assert result.summary["allow_strategy_integration_now"] is False
