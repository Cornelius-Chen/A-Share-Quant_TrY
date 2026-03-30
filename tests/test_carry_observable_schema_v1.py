from __future__ import annotations

from a_share_quant.strategy.carry_observable_schema_v1 import (
    CarryObservableSchemaAnalyzer,
)


def test_carry_observable_schema_extracts_row_level_fields() -> None:
    design_payload = {
        "summary": {
            "do_open_carry_factor_design": True,
            "row_isolation_required": True,
        }
    }
    mechanism_payload = {
        "mechanism_rows": [
            {
                "mechanism_type": "carry_in_basis_advantage",
                "trigger_date": "2024-11-05",
                "incumbent_cycle": {
                    "entry_date": "2024-11-06",
                    "exit_date": "2024-11-07",
                    "entry_price": 252.23,
                    "exit_price": 251.24,
                    "holding_days": 1,
                },
                "closest_challenger_cycle": {
                    "entry_date": "2024-11-05",
                    "exit_date": "2024-11-07",
                    "entry_price": 243.82,
                    "exit_price": 251.24,
                    "holding_days": 2,
                },
                "pnl_delta_vs_closest": 841.2523,
            }
        ]
    }

    result = CarryObservableSchemaAnalyzer().analyze(
        design_payload=design_payload,
        mechanism_b_payload=mechanism_payload,
        mechanism_c_payload=mechanism_payload,
    )

    assert result.summary["schema_posture"] == "open_carry_observable_schema_v1"
    assert result.summary["observable_mode"] == "negative_cycle_basis_row"
    assert result.summary["allow_scoring_design_next"] is True
    assert result.summary["same_exit_consistency"] is True
    assert result.summary["common_carry_days"] is True
    assert "basis_advantage_bps" in result.summary["required_fields"]


def test_carry_observable_schema_requires_open_row_isolated_design() -> None:
    design_payload = {
        "summary": {
            "do_open_carry_factor_design": True,
            "row_isolation_required": False,
        }
    }
    mechanism_payload = {"mechanism_rows": []}

    try:
        CarryObservableSchemaAnalyzer().analyze(
            design_payload=design_payload,
            mechanism_b_payload=mechanism_payload,
            mechanism_c_payload=mechanism_payload,
        )
    except ValueError as exc:
        assert "row-isolated" in str(exc)
    else:
        raise AssertionError("Expected row-isolated design requirement failure.")
