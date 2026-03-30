from __future__ import annotations

from a_share_quant.strategy.carry_factor_pilot_v1 import CarryFactorPilotAnalyzer


def test_carry_factor_pilot_opens_report_only_when_scores_are_identical() -> None:
    scoring_payload = {
        "summary": {"allow_factor_pilot_next": True},
        "score_rows": [
            {"strategy_name": "mainline_trend_b", "carry_score_v1": 1.0},
            {"strategy_name": "mainline_trend_c", "carry_score_v1": 1.0},
        ],
    }
    schema_payload = {
        "summary": {"schema_row_count": 2},
        "schema_rows": [{}, {}],
    }

    result = CarryFactorPilotAnalyzer().analyze(
        scoring_payload=scoring_payload,
        schema_payload=schema_payload,
    )

    assert result.summary["acceptance_posture"] == "open_carry_factor_pilot_as_report_only"
    assert result.summary["allow_report_only_pilot_now"] is True
    assert result.summary["allow_rankable_pilot_now"] is False
    assert result.summary["needs_more_row_diversity_for_rankable_pilot"] is True


def test_carry_factor_pilot_allows_rankable_mode_when_scores_diverge() -> None:
    scoring_payload = {
        "summary": {"allow_factor_pilot_next": True},
        "score_rows": [
            {"strategy_name": "mainline_trend_b", "carry_score_v1": 1.0},
            {"strategy_name": "mainline_trend_c", "carry_score_v1": 0.7},
            {"strategy_name": "mainline_trend_a", "carry_score_v1": 0.4},
        ],
    }
    schema_payload = {
        "summary": {"schema_row_count": 3},
        "schema_rows": [{}, {}, {}],
    }

    result = CarryFactorPilotAnalyzer().analyze(
        scoring_payload=scoring_payload,
        schema_payload=schema_payload,
    )

    assert result.summary["acceptance_posture"] == "open_carry_factor_pilot_as_rankable_micro_pilot"
    assert result.summary["allow_rankable_pilot_now"] is True
    assert result.summary["score_dispersion_present"] is True
