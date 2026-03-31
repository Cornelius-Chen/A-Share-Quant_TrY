from pathlib import Path

from a_share_quant.strategy.v112bd_market_regime_overlay_feature_review_v1 import (
    V112BDMarketRegimeOverlayFeatureReviewAnalyzer,
    load_json_report,
)


def test_v112bd_overlay_review_freezes_family() -> None:
    analyzer = V112BDMarketRegimeOverlayFeatureReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bd_phase_charter_v1.json")),
        v112af_feature_family_payload=load_json_report(Path("reports/analysis/v112af_cpo_feature_family_design_review_v1.json")),
        v113c_state_usage_payload=load_json_report(Path("reports/analysis/v113c_bounded_state_usage_review_v1.json")),
    )
    assert result.summary["overlay_feature_count"] == 10
    assert result.summary["formal_signal_generation_now"] is False
