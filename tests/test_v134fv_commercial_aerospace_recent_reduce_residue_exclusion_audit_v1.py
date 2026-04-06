from pathlib import Path

from a_share_quant.strategy.v134fv_commercial_aerospace_recent_reduce_residue_exclusion_audit_v1 import (
    V134FVCommercialAerospaceRecentReduceResidueExclusionAuditV1Analyzer,
)


def test_v134fv_commercial_aerospace_recent_reduce_residue_exclusion_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FVCommercialAerospaceRecentReduceResidueExclusionAuditV1Analyzer(repo_root).analyze()

    assert result.summary["candidate_count"] == 3
    assert result.summary["excluded_count"] == 1
    assert result.summary["excluded_displaced_count"] == 1
    assert result.summary["excluded_selected_count"] == 0
    assert result.summary["kept_selected_count"] == 2
    assert result.summary["kept_displaced_count"] == 0
    assert result.summary["displaced_precision"] == 1.0
    assert result.summary["displaced_coverage"] == 1.0
