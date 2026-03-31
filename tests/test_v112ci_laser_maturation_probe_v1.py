from pathlib import Path

from a_share_quant.strategy.v112ci_laser_maturation_probe_v1 import (
    V112CILaserMaturationProbeAnalyzer,
    load_json_report,
)


def test_v112ci_laser_maturation_probe_runs() -> None:
    analyzer = V112CILaserMaturationProbeAnalyzer()
    result = analyzer.analyze(
        by_payload=load_json_report(Path("reports/analysis/v112by_enabler_family_balance_band_transfer_probe_v1.json")),
        bp_payload=load_json_report(Path("reports/analysis/v112bp_cpo_selector_maturity_fusion_pilot_v1.json")),
        ch_payload=load_json_report(Path("reports/analysis/v112ch_packaging_mainline_template_freeze_v1.json")),
    )
    assert result.summary["sample_count"] == 4
