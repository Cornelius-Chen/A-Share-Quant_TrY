from pathlib import Path

from a_share_quant.strategy.v132i_commercial_aerospace_local_1min_rule_false_positive_audit_v1 import (
    V132ICommercialAerospaceLocal1MinRuleFalsePositiveAuditAnalyzer,
)


def test_v132i_local_1min_rule_false_positive_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132ICommercialAerospaceLocal1MinRuleFalsePositiveAuditAnalyzer(repo_root).analyze()

    assert result.summary["buy_execution_row_count"] == 55
    assert result.summary["seed_row_count"] == 6
    assert result.summary["seed_match_count"] == 6

