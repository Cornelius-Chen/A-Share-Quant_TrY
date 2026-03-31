from __future__ import annotations

from a_share_quant.strategy.v112d_sidecar_pilot_v1 import V112DSidecarPilotAnalyzer
from a_share_quant.strategy import v112d_sidecar_pilot_v1 as mod


class _FakeClient:
    class _DummyFrame:
        def copy(self):
            return self

    def fetch_daily_bars(self, symbol: str):  # pragma: no cover - dummy stub only
        return self._DummyFrame()


def test_v112d_sidecar_pilot_runs_models(monkeypatch) -> None:
    monkeypatch.setattr(mod, "TencentKlineClient", _FakeClient)
    monkeypatch.setattr(
        mod.V112BBaselineReadoutAnalyzer,
        "_build_symbol_samples",
        lambda self, symbol, cycle_window, bars: [
            mod.TrainingSample(
                trade_date=f"2023-02-{idx + 1:02d}",
                symbol=symbol,
                stage="major_markup" if idx % 3 == 0 else "high_level_consolidation" if idx % 3 == 1 else "deep_box_reset",
                label="carry_constructive" if idx % 3 == 0 else "failed" if idx % 3 == 1 else "watch_constructive",
                feature_values={name: float((idx % 5) + j) for j, name in enumerate(mod.V112BBaselineReadoutAnalyzer.FEATURE_NAMES)},
                forward_return_20d=0.2,
                max_drawdown_20d=-0.05,
                forward_return_bucket="strong_up",
                max_drawdown_bucket="contained",
            )
            for idx in range(45)
        ],
    )
    result = V112DSidecarPilotAnalyzer().analyze(
        phase_charter_payload={"summary": {"ready_for_sidecar_pilot_next": True}},
        pilot_dataset_payload={
            "dataset_rows": [
                {"symbol": "300308", "cycle_window": {"first_markup_start": "2023-02", "first_markup_end": "2023-06", "cooling_and_box_start": "2023-07", "cooling_and_box_end": "2024-01", "major_markup_start": "2024-02", "major_markup_end": "2024-05"}},
                {"symbol": "300502", "cycle_window": {"first_markup_start": "2023-02", "first_markup_end": "2023-05", "long_box_reset_start": "2023-06", "long_box_reset_end": "2024-01", "major_markup_start": "2024-02", "major_markup_end": "2024-05"}},
                {"symbol": "300394", "cycle_window": {"first_markup_start": "2023-02", "first_markup_end": "2023-06", "deep_box_reset_start": "2023-07", "deep_box_reset_end": "2024-01", "major_markup_start": "2024-02", "major_markup_end": "2024-05"}},
            ]
        },
        training_protocol_payload={"summary": {"acceptance_posture": "freeze_v112_training_protocol_v1"}},
        baseline_readout_payload={
            "summary": {"test_accuracy": 0.4},
            "fold_rows": [
                {"stage": "major_markup", "predicted_label": "carry_constructive", "true_label": "failed"},
                {"stage": "high_level_consolidation", "predicted_label": "carry_constructive", "true_label": "failed"},
            ],
        },
        sidecar_protocol_payload={"summary": {"candidate_model_family_count": 2}},
    )

    assert result.summary["model_count"] == 2
    assert result.summary["ready_for_phase_check_next"] is True
    assert all(row["same_dataset_rule_kept"] for row in result.model_rows)
