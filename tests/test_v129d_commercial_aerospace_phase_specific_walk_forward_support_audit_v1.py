from pathlib import Path

from a_share_quant.strategy.v129d_commercial_aerospace_phase_specific_walk_forward_support_audit_v1 import (
    V129DCommercialAerospacePhaseSpecificWalkForwardSupportAuditAnalyzer,
)


def test_v129d_commercial_aerospace_phase_specific_walk_forward_support_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129DCommercialAerospacePhaseSpecificWalkForwardSupportAuditAnalyzer(repo_root).analyze()

    assert result.summary["fold_count"] == 3
    assert len(result.fold_rows) == 3
    assert "full_pre_dedicated_fold" in result.summary["supported_folds"]
