from pathlib import Path

from a_share_quant.strategy.v129j_commercial_aerospace_ij_late_preheat_governance_triage_v1 import (
    V129JCommercialAerospaceIJLatePreheatGovernanceTriageAnalyzer,
)


def test_v129j_commercial_aerospace_ij_late_preheat_governance_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129JCommercialAerospaceIJLatePreheatGovernanceTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] in {
        "retain_governance_rule_and_failure_cases",
        "no_mismatch_found",
    }
