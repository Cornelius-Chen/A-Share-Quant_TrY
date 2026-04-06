from pathlib import Path

from a_share_quant.strategy.v132u_commercial_aerospace_local_1min_state_transition_audit_v1 import (
    V132UCommercialAerospaceLocal1MinStateTransitionAuditAnalyzer,
)


def test_v132u_local_1min_state_transition_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V132UCommercialAerospaceLocal1MinStateTransitionAuditAnalyzer(repo_root).analyze()

    assert report.summary["hit_row_count"] == 24
    assert report.summary["unique_transition_pattern_count"] > 0
    assert report.summary["severe_hits_with_prior_reversal_share"] >= 0.0

