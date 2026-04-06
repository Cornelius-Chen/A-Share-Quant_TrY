from pathlib import Path

from a_share_quant.strategy.v131u_commercial_aerospace_local_5min_override_coverage_audit_v1 import (
    V131UCommercialAerospaceLocal5MinOverrideCoverageAuditAnalyzer,
)


def test_v131u_local_5min_override_coverage_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131UCommercialAerospaceLocal5MinOverrideCoverageAuditAnalyzer(repo_root).analyze()

    assert result.summary["buy_execution_row_count"] == 55
    assert result.summary["true_positive_seed_hits"] == 4
    assert result.summary["non_override_flagged_count"] == 2
    assert result.summary["ambiguous_hit_count"] == 2
    assert result.summary["ambiguous_total"] == 19
    assert result.summary["clean_control_hit_count"] == 0
    assert result.summary["clean_control_total"] == 30

