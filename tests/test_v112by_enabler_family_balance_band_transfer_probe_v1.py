from pathlib import Path

from a_share_quant.strategy.v112by_enabler_family_balance_band_transfer_probe_v1 import (
    V112BYEnablerFamilyBalanceBandTransferProbeAnalyzer,
    load_json_report,
)


def test_v112by_transfer_probe_runs() -> None:
    analyzer = V112BYEnablerFamilyBalanceBandTransferProbeAnalyzer()
    result = analyzer.analyze(
        bx_payload=load_json_report(Path("reports/analysis/v112bx_packaging_process_enabler_balance_band_review_v1.json")),
        bp_payload=load_json_report(Path("reports/analysis/v112bp_cpo_selector_maturity_fusion_pilot_v1.json")),
        az_payload=load_json_report(Path("reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json")),
    )
    assert result.summary["sample_count"] > 0
