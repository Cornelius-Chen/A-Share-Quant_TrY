from __future__ import annotations

from a_share_quant.strategy.v12_next_refresh_factor_diversity_design_v1 import (
    V12NextRefreshFactorDiversityDesignAnalyzer,
)


def test_v12_next_refresh_design_opens_when_row_diversity_gap_exists() -> None:
    phase_readiness_payload = {
        "summary": {
            "do_open_new_refresh_batch_now": True,
        }
    }
    carry_pilot_payload = {
        "summary": {
            "needs_more_row_diversity_for_rankable_pilot": True,
            "distinct_score_count": 1,
        }
    }
    carry_schema_payload = {
        "summary": {
            "schema_row_count": 2,
        }
    }

    result = V12NextRefreshFactorDiversityDesignAnalyzer().analyze(
        phase_readiness_payload=phase_readiness_payload,
        carry_pilot_payload=carry_pilot_payload,
        carry_schema_payload=carry_schema_payload,
    )

    assert result.summary["design_posture"] == "prepare_refresh_batch_for_factor_row_diversity"
    assert result.summary["do_prepare_new_refresh_manifest"] is True
    assert result.summary["target_count"] == 4


def test_v12_next_refresh_design_requires_refresh_need() -> None:
    phase_readiness_payload = {"summary": {"do_open_new_refresh_batch_now": False}}
    carry_pilot_payload = {"summary": {"needs_more_row_diversity_for_rankable_pilot": True}}
    carry_schema_payload = {"summary": {"schema_row_count": 2}}

    try:
        V12NextRefreshFactorDiversityDesignAnalyzer().analyze(
            phase_readiness_payload=phase_readiness_payload,
            carry_pilot_payload=carry_pilot_payload,
            carry_schema_payload=carry_schema_payload,
        )
    except ValueError as exc:
        assert "later refresh batch" in str(exc)
    else:
        raise AssertionError("Expected next refresh design gate failure.")
