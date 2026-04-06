from pathlib import Path

from a_share_quant.strategy.v125i_commercial_aerospace_event_conditioned_control_surface_refresh_v1 import (
    V125ICommercialAerospaceEventConditionedControlSurfaceRefreshAnalyzer,
)


def test_v125i_scans_multiple_event_conditioned_variants() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125ICommercialAerospaceEventConditionedControlSurfaceRefreshAnalyzer(repo_root).analyze()
    assert result.summary["variant_count"] == 4
    assert result.summary["control_core_count"] >= 10
