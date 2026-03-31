from __future__ import annotations

from a_share_quant.strategy import v112e_gbdt_attribution_review_v1 as mod
from a_share_quant.strategy.v112e_gbdt_attribution_review_v1 import (
    V112EGBDTAttributionReviewAnalyzer,
)


class _FakeClient:
    class _DummyFrame:
        def copy(self):
            return self

    def fetch_daily_bars(self, symbol: str):
        return self._DummyFrame()


def test_v112e_attribution_review_outputs_block_rows(monkeypatch) -> None:
    monkeypatch.setattr(mod, "TencentKlineClient", _FakeClient)
    monkeypatch.setattr(
        mod.V112BBaselineReadoutAnalyzer,
        "_build_symbol_samples",
        lambda self, symbol, cycle_window, bars: [
            mod.TrainingSample(
                trade_date=f"2023-02-{idx + 1:02d}",
                symbol=symbol,
                stage="major_markup" if idx % 2 == 0 else "high_level_consolidation",
                label="carry_constructive" if idx % 3 == 0 else "failed" if idx % 3 == 1 else "watch_constructive",
                feature_values={name: float((idx % 7) + j) for j, name in enumerate(mod.V112BBaselineReadoutAnalyzer.FEATURE_NAMES)},
                forward_return_20d=0.2,
                max_drawdown_20d=-0.05,
                forward_return_bucket="strong_up",
                max_drawdown_bucket="contained",
            )
            for idx in range(60)
        ],
    )
    result = V112EGBDTAttributionReviewAnalyzer().analyze(
        phase_charter_payload={"summary": {"ready_for_attribution_review_next": True}},
        pilot_dataset_payload={"dataset_rows": [{"symbol": "300308", "cycle_window": {}}, {"symbol": "300502", "cycle_window": {}}, {"symbol": "300394", "cycle_window": {}}]},
        baseline_readout_payload={
            "summary": {"test_accuracy": 0.45},
            "fold_rows": [
                {"stage": "major_markup", "predicted_label": "carry_constructive", "true_label": "failed"},
                {"stage": "high_level_consolidation", "predicted_label": "carry_constructive", "true_label": "failed"},
            ],
        },
    )

    assert result.summary["block_count"] == 4
    assert len(result.block_ablation_rows) == 4
    assert result.summary["ready_for_phase_check_next"] is True
