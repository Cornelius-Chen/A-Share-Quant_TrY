from pathlib import Path

from a_share_quant.strategy.v134fl_commercial_aerospace_full_quality_module_portability_audit_v1 import (
    V134FLCommercialAerospaceFullQualityModulePortabilityAuditV1Analyzer,
)


def test_v134fl_commercial_aerospace_full_quality_module_portability_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FLCommercialAerospaceFullQualityModulePortabilityAuditV1Analyzer(repo_root).analyze()

    assert result.summary["scenario_count"] == 5
    assert result.summary["best_scenario_name"] == "unlock_high_role_full_archetype_with_burst"
    assert result.summary["best_scenario_non_seed_to_seed_ratio"] == 1.5
    assert result.summary["best_scenario_seed_kept_count"] == 2
    assert result.summary["best_scenario_non_seed_kept_count"] == 3
