from pathlib import Path

from a_share_quant.strategy.v125g_commercial_aerospace_clean_boundary_control_surface_refresh_v1 import (
    V125GCommercialAerospaceCleanBoundaryControlSurfaceRefreshAnalyzer,
)


def test_v125g_scans_multiple_clean_boundary_variants() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125GCommercialAerospaceCleanBoundaryControlSurfaceRefreshAnalyzer(repo_root).analyze()
    assert result.summary["variant_count"] == 4
