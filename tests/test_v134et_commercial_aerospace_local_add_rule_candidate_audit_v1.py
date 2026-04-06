from pathlib import Path

from a_share_quant.strategy.v134et_commercial_aerospace_local_add_rule_candidate_audit_v1 import (
    V134ETCommercialAerospaceLocalAddRuleCandidateAuditV1Analyzer,
)


def test_v134et_commercial_aerospace_local_add_rule_candidate_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134ETCommercialAerospaceLocalAddRuleCandidateAuditV1Analyzer(repo_root).analyze()

    assert result.summary["registry_row_count"] == 55
    assert result.summary["matched_count"] == 55
    assert result.summary["unmatched_count"] == 0
