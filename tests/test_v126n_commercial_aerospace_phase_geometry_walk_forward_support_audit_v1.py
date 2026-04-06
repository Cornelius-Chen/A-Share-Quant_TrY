from pathlib import Path

from a_share_quant.strategy.v126n_commercial_aerospace_phase_geometry_walk_forward_support_audit_v1 import (
    V126NCommercialAerospacePhaseGeometryWalkForwardSupportAuditAnalyzer,
)


def test_v126n_walk_forward_support_audit_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126NCommercialAerospacePhaseGeometryWalkForwardSupportAuditAnalyzer(repo_root).analyze()
    assert result.summary["matured_full_count_on_20251224"] >= 0
    assert result.summary["matured_full_count_on_20260108"] >= result.summary["matured_full_count_on_20251224"]
