from pathlib import Path

from a_share_quant.strategy.v126l_commercial_aerospace_full_eligibility_support_gap_audit_v1 import (
    V126LCommercialAerospaceFullEligibilitySupportGapAuditAnalyzer,
)


def test_v126l_full_support_gap_audit_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126LCommercialAerospaceFullEligibilitySupportGapAuditAnalyzer(repo_root).analyze()
    assert result.summary["test_full_count"] > 0
    assert result.summary["impulse_continuation_train_full_count"] == 0
