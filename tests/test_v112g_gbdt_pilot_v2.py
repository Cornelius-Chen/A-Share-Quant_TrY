from __future__ import annotations

from a_share_quant.strategy import v112g_gbdt_pilot_v2 as mod
from a_share_quant.strategy.v112b_baseline_readout_v1 import TrainingSample
from a_share_quant.strategy.v112g_gbdt_pilot_v2 import V112GGBDTPilotV2Analyzer


def test_v112g_gbdt_pilot_v2_compares_against_v1() -> None:
    synthetic_samples = [
        TrainingSample(
            trade_date=f"2024-01-{idx + 1:02d}",
            symbol="300308" if idx % 3 == 0 else "300502" if idx % 3 == 1 else "300394",
            stage="major_markup" if idx % 2 == 0 else "high_level_consolidation",
            label="carry_constructive" if idx % 3 == 0 else "failed" if idx % 3 == 1 else "watch_constructive",
            feature_values={name: float((idx % 5) + j) for j, name in enumerate(mod.V112GBaselineReadoutV2Analyzer.FEATURE_NAMES)},
            forward_return_20d=0.2,
            max_drawdown_20d=-0.05,
            forward_return_bucket="strong_up",
            max_drawdown_bucket="contained",
        )
        for idx in range(90)
    ]

    class _FakeAnalyzer:
        FEATURE_NAMES = mod.V112GBaselineReadoutV2Analyzer.FEATURE_NAMES

        def build_augmented_samples(self, *, pilot_dataset_payload, bar_frames_by_symbol=None):
            return synthetic_samples

    original = mod.V112GBaselineReadoutV2Analyzer
    mod.V112GBaselineReadoutV2Analyzer = _FakeAnalyzer
    try:
        result = V112GGBDTPilotV2Analyzer().analyze(
            phase_charter_payload={"summary": {"ready_for_feature_schema_v2_next": True}},
            pilot_dataset_payload={"dataset_rows": [{"symbol": "300308"}]},
            baseline_v1_payload={"summary": {"test_accuracy": 0.4509}},
            gbdt_v1_payload={"model_rows": [{"model_name": "hist_gradient_boosting_classifier", "test_accuracy": 0.558, "false_positive_count_in_major_markup": 125, "false_positive_count_in_high_level_consolidation": 1}]},
            baseline_v2_payload={"summary": {"baseline_v2_test_accuracy": 0.5}},
        )
    finally:
        mod.V112GBaselineReadoutV2Analyzer = original

    assert result.summary["gbdt_v1_test_accuracy"] == 0.558
    assert result.summary["ready_for_phase_check_next"] is True
