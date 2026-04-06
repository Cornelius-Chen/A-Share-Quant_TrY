from pathlib import Path

from a_share_quant.strategy.v125a_commercial_aerospace_control_surface_time_split_audit_v1 import (
    V125ACommercialAerospaceControlSurfaceTimeSplitAuditAnalyzer,
)


def test_v125a_has_year_splits() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125ACommercialAerospaceControlSurfaceTimeSplitAuditAnalyzer(repo_root).analyze()
    assert result.summary["year_count"] >= 2
