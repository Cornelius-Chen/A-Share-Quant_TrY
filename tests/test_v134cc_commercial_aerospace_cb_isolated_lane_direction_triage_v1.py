from pathlib import Path

from a_share_quant.strategy.v134cb_commercial_aerospace_isolated_sell_side_shadow_lane_v1 import (
    V134CBCommercialAerospaceIsolatedSellSideShadowLaneV1Analyzer,
    write_report as write_lane_report,
)
from a_share_quant.strategy.v134cc_commercial_aerospace_cb_isolated_lane_direction_triage_v1 import (
    V134CCCommercialAerospaceCBIsolatedLaneDirectionTriageV1Analyzer,
)


def test_v134cc_commercial_aerospace_cb_isolated_lane_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    lane = V134CBCommercialAerospaceIsolatedSellSideShadowLaneV1Analyzer(repo_root).analyze()
    write_lane_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cb_commercial_aerospace_isolated_sell_side_shadow_lane_v1",
        result=lane,
    )

    result = V134CCCommercialAerospaceCBIsolatedLaneDirectionTriageV1Analyzer(repo_root).analyze()
    assert (
        result.summary["authoritative_status"]
        == "retain_isolated_sell_side_shadow_lane_and_audit_binding_quality_next"
    )
    assert result.summary["executed_session_count"] == 12
