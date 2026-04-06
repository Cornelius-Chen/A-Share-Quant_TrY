from pathlib import Path

from a_share_quant.strategy.v134fj_commercial_aerospace_full_quality_add_archetype_audit_v1 import (
    V134FJCommercialAerospaceFullQualityAddArchetypeAuditV1Analyzer,
)


def test_v134fj_commercial_aerospace_full_quality_add_archetype_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FJCommercialAerospaceFullQualityAddArchetypeAuditV1Analyzer(repo_root).analyze()

    assert result.summary["threshold_row_count"] == 6
    assert result.summary["best_close_loc_15m_threshold"] == 0.63
    assert result.summary["best_full_quality_hit_count"] == 5
    assert result.summary["best_counterfactual_hit_count"] == 0
    assert result.summary["best_precision"] == 1.0
    assert result.summary["best_coverage"] == 1.0
