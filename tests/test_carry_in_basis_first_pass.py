from __future__ import annotations

from a_share_quant.strategy.carry_in_basis_first_pass import (
    CarryInBasisFirstPassAnalyzer,
)


def test_carry_in_basis_first_pass_opens_bounded_lane_when_evidence_is_clean() -> None:
    protocol_payload = {
        "factor_rows": [
            {
                "entry_name": "carry_in_basis_advantage",
                "evaluation_bucket": "evaluate_now",
                "protocol_posture": "promote_into_first_pass_factor_evaluation",
            }
        ]
    }
    family_inventory_payload = {
        "family_rows": [
            {
                "family_name": "carry_in_basis_advantage",
                "occurrence_count": 2,
                "report_count": 2,
                "net_family_edge": 1682.5,
                "positive_opportunity_cost": 0.0,
            }
        ]
    }
    cross_strategy_payload = {
        "summary": {"identical_negative_cycle_map": True},
        "shared_mechanisms": [
            {"mechanism_type": "carry_in_basis_advantage", "shared_strategy_count": 2}
        ],
    }
    mechanism_payload = {
        "mechanism_rows": [
            {"mechanism_type": "carry_in_basis_advantage", "cycle_sign": "negative"}
        ]
    }

    result = CarryInBasisFirstPassAnalyzer().analyze(
        protocol_payload=protocol_payload,
        family_inventory_payload=family_inventory_payload,
        cross_strategy_payload=cross_strategy_payload,
        mechanism_b_payload=mechanism_payload,
        mechanism_c_payload=mechanism_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "open_carry_in_basis_first_pass_as_bounded_factor_candidate"
    )
    assert result.summary["do_open_bounded_carry_factor_lane"] is True
    assert result.summary["promote_to_retained_feature_now"] is False


def test_carry_in_basis_first_pass_holds_without_cross_strategy_reuse() -> None:
    protocol_payload = {
        "factor_rows": [
            {
                "entry_name": "carry_in_basis_advantage",
                "evaluation_bucket": "evaluate_now",
                "protocol_posture": "promote_into_first_pass_factor_evaluation",
            }
        ]
    }
    family_inventory_payload = {
        "family_rows": [
            {
                "family_name": "carry_in_basis_advantage",
                "occurrence_count": 2,
                "report_count": 2,
                "net_family_edge": 1682.5,
                "positive_opportunity_cost": 0.0,
            }
        ]
    }
    cross_strategy_payload = {"shared_mechanisms": []}
    mechanism_payload = {
        "mechanism_rows": [
            {"mechanism_type": "carry_in_basis_advantage", "cycle_sign": "negative"}
        ]
    }

    result = CarryInBasisFirstPassAnalyzer().analyze(
        protocol_payload=protocol_payload,
        family_inventory_payload=family_inventory_payload,
        cross_strategy_payload=cross_strategy_payload,
        mechanism_b_payload=mechanism_payload,
        mechanism_c_payload=mechanism_payload,
    )

    assert result.summary["acceptance_posture"] == "hold_carry_in_basis_before_factor_design"
    assert result.summary["do_open_bounded_carry_factor_lane"] is False
