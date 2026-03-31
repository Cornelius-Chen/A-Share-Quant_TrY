from __future__ import annotations

from a_share_quant.strategy.v112f_phase_check_v1 import V112FPhaseCheckAnalyzer


def test_v112f_phase_check_reports_refinement_success() -> None:
    result = V112FPhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112f_now": True}},
        refinement_design_payload={
            "summary": {
                "ready_for_phase_check_next": True,
                "primary_bottleneck_type": "feature_definition_or_non_redundancy_gap",
                "most_useful_block_by_hotspot_impact": "catalyst_state",
            }
        },
    )

    assert result.summary["refinement_design_present"] is True
    assert result.summary["ready_for_phase_closure_next"] is True
