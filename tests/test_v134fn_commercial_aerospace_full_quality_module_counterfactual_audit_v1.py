from pathlib import Path

from a_share_quant.strategy.v134fn_commercial_aerospace_full_quality_module_counterfactual_audit_v1 import (
    V134FNCommercialAerospaceFullQualityModuleCounterfactualAuditV1Analyzer,
)


def test_v134fn_commercial_aerospace_full_quality_module_counterfactual_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FNCommercialAerospaceFullQualityModuleCounterfactualAuditV1Analyzer(repo_root).analyze()

    assert result.summary["scenario_name"] == "unlock_high_role_full_archetype_with_burst"
    assert result.summary["matched_session_count"] == 5
    assert result.summary["seed_match_count"] == 2
    assert result.summary["counterfactual_count"] == 3
    assert result.summary["selection_displacement_counterfactual_count"] == 1
    assert result.summary["no_order_day_post_seed_echo_count"] == 2
    assert result.summary["mean_trading_days_since_prior_allowed_seed"] == 7.66666667
