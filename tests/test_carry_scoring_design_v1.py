from __future__ import annotations

from a_share_quant.strategy.carry_scoring_design_v1 import CarryScoringDesignAnalyzer


def test_carry_scoring_design_builds_score_rows() -> None:
    schema_payload = {
        "summary": {"allow_scoring_design_next": True},
        "schema_rows": [
            {
                "strategy_name": "mainline_trend_b",
                "basis_advantage_bps": 300.0,
                "same_exit_date": True,
                "challenger_carry_days": 1,
                "pnl_delta_vs_closest": 900.0,
            },
            {
                "strategy_name": "mainline_trend_c",
                "basis_advantage_bps": 150.0,
                "same_exit_date": True,
                "challenger_carry_days": 1,
                "pnl_delta_vs_closest": 400.0,
            },
        ],
    }

    result = CarryScoringDesignAnalyzer().analyze(schema_payload=schema_payload)

    assert result.summary["design_posture"] == "open_carry_scoring_design_v1"
    assert result.summary["allow_factor_pilot_next"] is True
    assert result.summary["allow_strategy_integration_now"] is False
    assert len(result.score_rows) == 2
    assert result.score_rows[0]["carry_score_v1"] > result.score_rows[1]["carry_score_v1"]


def test_carry_scoring_design_requires_schema_transition() -> None:
    schema_payload = {"summary": {"allow_scoring_design_next": False}, "schema_rows": [{}]}

    try:
        CarryScoringDesignAnalyzer().analyze(schema_payload=schema_payload)
    except ValueError as exc:
        assert "schema-to-scoring transition" in str(exc)
    else:
        raise AssertionError("Expected schema transition failure.")
