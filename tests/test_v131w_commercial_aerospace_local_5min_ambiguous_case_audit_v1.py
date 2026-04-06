from pathlib import Path

from a_share_quant.strategy.v131w_commercial_aerospace_local_5min_ambiguous_case_audit_v1 import (
    V131WCommercialAerospaceLocal5MinAmbiguousCaseAuditAnalyzer,
)


def test_v131w_local_5min_ambiguous_case_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131WCommercialAerospaceLocal5MinAmbiguousCaseAuditAnalyzer(repo_root).analyze()

    assert result.summary["flagged_non_override_case_count"] == 2
    assert result.summary["mild_override_watch_count"] == 2
    assert result.summary["documented_false_positive_count"] == 0

