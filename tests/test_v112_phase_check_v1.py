from __future__ import annotations

from a_share_quant.strategy.v112_phase_check_v1 import V112PhaseCheckAnalyzer


def test_v112_phase_check_keeps_phase_definition_only() -> None:
    result = V112PhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112_now": True}},
        pilot_cycle_selection_payload={
            "summary": {
                "selected_primary_family": "earnings_transmission_carry",
                "selected_pilot_cycle": "optical_link_price_and_demand_upcycle",
            }
        },
        training_protocol_payload={"summary": {"feature_block_count": 4, "label_count": 3, "validation_rule_count": 4}},
    )

    assert result.summary["ready_for_bounded_pilot_data_assembly_next"] is True
    assert result.summary["allow_strategy_integration_now"] is False
    assert result.summary["allow_black_box_deployment_now"] is False
