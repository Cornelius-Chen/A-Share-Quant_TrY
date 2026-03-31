from pathlib import Path

from a_share_quant.strategy.v112bx_packaging_process_enabler_balance_band_review_v1 import (
    V112BXPackagingProcessEnablerBalanceBandReviewAnalyzer,
    load_json_report,
)


def test_v112bx_balance_band_review_runs() -> None:
    analyzer = V112BXPackagingProcessEnablerBalanceBandReviewAnalyzer()
    result = analyzer.analyze(
        bw_payload=load_json_report(Path("reports/analysis/v112bw_packaging_process_enabler_contrastive_control_pilot_v1.json")),
    )
    assert result.summary["classification_accuracy"] == 1.0
