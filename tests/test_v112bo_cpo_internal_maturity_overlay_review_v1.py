from pathlib import Path

from a_share_quant.strategy.v112bo_cpo_internal_maturity_overlay_review_v1 import (
    V112BOCPOInternalMaturityOverlayReviewAnalyzer,
    load_json_report,
)


def test_v112bo_overlay_review_freezes_internal_family() -> None:
    analyzer = V112BOCPOInternalMaturityOverlayReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bo_phase_charter_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
        market_regime_overlay_payload=load_json_report(Path("reports/analysis/v112bd_market_regime_overlay_feature_review_v1.json")),
        feature_family_payload=load_json_report(Path("reports/analysis/v112af_cpo_feature_family_design_review_v1.json")),
        regime_gate_pilot_payload=load_json_report(Path("reports/analysis/v112bl_cpo_regime_aware_gate_pilot_v1.json")),
    )
    assert result.summary["overlay_feature_count"] == 8
    assert result.summary["formal_signal_generation_now"] is False
