from pathlib import Path

from a_share_quant.strategy.v134bw_commercial_aerospace_start_of_day_sell_binding_surface_spec_v1 import (
    V134BWCommercialAerospaceStartOfDaySellBindingSurfaceSpecV1Analyzer,
)


def test_v134bw_commercial_aerospace_start_of_day_sell_binding_surface_spec_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134BWCommercialAerospaceStartOfDaySellBindingSurfaceSpecV1Analyzer(repo_root).analyze()

    assert result.summary["broader_hit_session_count"] == 24
    assert result.summary["fully_funded_overlap_count"] == 1
    assert result.summary["must_build_component_count"] == 5
    assert any(
        row["surface_component"] == "same_day_new_lots_bucket" and row["status"] == "must_build"
        for row in result.spec_rows
    )
