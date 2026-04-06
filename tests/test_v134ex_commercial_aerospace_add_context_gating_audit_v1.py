from pathlib import Path

from a_share_quant.strategy.v134ex_commercial_aerospace_add_context_gating_audit_v1 import (
    V134EXCommercialAerospaceAddContextGatingAuditV1Analyzer,
)


def test_v134ex_commercial_aerospace_add_context_gating_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134EXCommercialAerospaceAddContextGatingAuditV1Analyzer(repo_root).analyze()

    assert result.summary["scenario_count"] == 7
    assert result.summary["baseline_non_seed_to_seed_ratio"] == 10.53191489
    assert result.summary["best_scenario_name"] == "unlock_worthy_plus_high_role"
    assert result.summary["best_scenario_non_seed_to_seed_ratio"] == 5.4
