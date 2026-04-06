from pathlib import Path

from a_share_quant.strategy.v134ff_commercial_aerospace_persistent_permission_confirmation_audit_v1 import (
    V134FFCommercialAerospacePersistentPermissionConfirmationAuditV1Analyzer,
)


def test_v134ff_commercial_aerospace_persistent_permission_confirmation_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FFCommercialAerospacePersistentPermissionConfirmationAuditV1Analyzer(repo_root).analyze()

    assert result.summary["threshold_row_count"] == 12
    assert result.summary["best_open_to_60m_threshold"] == 0.01
    assert result.summary["best_continuation_threshold"] == 0.005
    assert result.summary["best_burst_amount_share_cap"] == 0.4
    assert result.summary["best_persistent_hit_count"] == 9
    assert result.summary["best_counterfactual_hit_count"] == 0
    assert result.summary["best_precision"] == 1.0
    assert result.summary["best_coverage"] == 0.9
