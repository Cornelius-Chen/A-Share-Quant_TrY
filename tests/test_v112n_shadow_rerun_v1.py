from pathlib import Path

from a_share_quant.strategy.v112n_shadow_rerun_v1 import V112NShadowRerunAnalyzer, load_json_report


def test_v112n_shadow_rerun_v1_stays_review_only_even_without_gain() -> None:
    result = V112NShadowRerunAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112n_phase_charter_v1.json")),
        pilot_dataset_payload=load_json_report(Path("reports/analysis/v112b_pilot_dataset_freeze_v1.json")),
        baseline_v2_payload=load_json_report(Path("reports/analysis/v112g_baseline_readout_v2.json")),
        gbdt_v2_payload=load_json_report(Path("reports/analysis/v112g_gbdt_pilot_v2.json")),
    )
    assert result.summary["shadow_feature_count"] == 3
    assert result.summary["baseline_shadow_test_accuracy"] == result.summary["baseline_v2_test_accuracy"]
    assert result.summary["gbdt_shadow_test_accuracy"] == result.summary["gbdt_v2_test_accuracy"]
