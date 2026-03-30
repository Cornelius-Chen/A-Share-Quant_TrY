from __future__ import annotations

from a_share_quant.strategy.carry_factor_design_v1 import CarryFactorDesignAnalyzer


def test_carry_factor_design_requires_row_isolation_in_mixed_shared_pocket() -> None:
    first_pass_payload = {
        "summary": {
            "do_open_bounded_carry_factor_lane": True,
        }
    }
    mechanism_payload = {
        "mechanism_rows": [
            {"mechanism_type": "carry_in_basis_advantage"},
            {"mechanism_type": "earlier_exit_loss_reduction"},
        ]
    }
    cross_strategy_payload = {
        "summary": {"identical_negative_cycle_map": True},
    }

    result = CarryFactorDesignAnalyzer().analyze(
        first_pass_payload=first_pass_payload,
        mechanism_b_payload=mechanism_payload,
        mechanism_c_payload=mechanism_payload,
        cross_strategy_payload=cross_strategy_payload,
    )

    assert result.summary["design_posture"] == "open_row_isolated_carry_factor_design"
    assert result.summary["row_isolation_required"] is True
    assert result.summary["allow_broad_factor_scoring_now"] is False
    assert result.summary["allow_retained_feature_promotion_now"] is False


def test_carry_factor_design_holds_when_first_pass_is_closed() -> None:
    first_pass_payload = {"summary": {"do_open_bounded_carry_factor_lane": False}}
    mechanism_payload = {"mechanism_rows": [{"mechanism_type": "carry_in_basis_advantage"}]}
    cross_strategy_payload = {"summary": {"identical_negative_cycle_map": True}}

    result = CarryFactorDesignAnalyzer().analyze(
        first_pass_payload=first_pass_payload,
        mechanism_b_payload=mechanism_payload,
        mechanism_c_payload=mechanism_payload,
        cross_strategy_payload=cross_strategy_payload,
    )

    assert result.summary["design_posture"] == "hold_carry_factor_design"
    assert result.summary["do_open_carry_factor_design"] is False
