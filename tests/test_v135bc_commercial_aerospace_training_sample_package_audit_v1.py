from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135bc_commercial_aerospace_training_sample_package_audit_v1 import (
    V135BCCommercialAerospaceTrainingSamplePackageAuditV1Analyzer,
)


def test_v135bc_training_sample_package_audit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135BCCommercialAerospaceTrainingSamplePackageAuditV1Analyzer(repo_root).analyze()
    assert result.summary["row_count"] == 10
    assert result.summary["primary_fit_count"] == 2
    assert result.summary["auxiliary_fit_count"] == 4
    assert result.summary["reference_only_count"] == 3
    assert result.summary["locked_holdout_count"] == 1
    assert result.summary["primary_positive_fit_count"] == 0
