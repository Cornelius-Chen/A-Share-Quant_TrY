from pathlib import Path

from a_share_quant.strategy.v112bd_phase_check_v1 import (
    V112BDPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bd_phase_check_keeps_overlay_boundary() -> None:
    analyzer = V112BDPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bd_phase_charter_v1.json")),
        review_payload=load_json_report(Path("reports/analysis/v112bd_market_regime_overlay_feature_review_v1.json")),
    )
    assert result.summary["overlay_feature_count"] == 10
