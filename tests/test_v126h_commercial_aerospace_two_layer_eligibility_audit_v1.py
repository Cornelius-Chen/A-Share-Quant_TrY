from pathlib import Path

from a_share_quant.strategy.v126h_commercial_aerospace_two_layer_eligibility_audit_v1 import (
    V126HCommercialAerospaceTwoLayerEligibilityAuditAnalyzer,
)


def test_v126h_two_layer_audit_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126HCommercialAerospaceTwoLayerEligibilityAuditAnalyzer(repo_root).analyze()
    assert result.summary["impulse_test_count"] > 0
    assert result.summary["impulse_train_full_count"] == 0
    assert len(result.variant_rows) == 3
