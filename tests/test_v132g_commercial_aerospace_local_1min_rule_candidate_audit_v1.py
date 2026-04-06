from pathlib import Path

from a_share_quant.strategy.v132g_commercial_aerospace_local_1min_rule_candidate_audit_v1 import (
    V132GCommercialAerospaceLocal1MinRuleCandidateAuditAnalyzer,
)


def test_v132g_local_1min_rule_candidate_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132GCommercialAerospaceLocal1MinRuleCandidateAuditAnalyzer(repo_root).analyze()

    assert result.summary["registry_row_count"] == 6
    assert result.summary["matched_count"] == 6
    assert result.summary["unmatched_count"] == 0

