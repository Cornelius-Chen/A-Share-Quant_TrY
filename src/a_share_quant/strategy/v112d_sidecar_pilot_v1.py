from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.neural_network import MLPClassifier

from a_share_quant.strategy.v112b_baseline_readout_v1 import (
    TrainingSample,
    V112BBaselineReadoutAnalyzer,
    load_json_report,
)
from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient


@dataclass(slots=True)
class V112DSidecarPilotReport:
    summary: dict[str, Any]
    model_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "model_rows": self.model_rows,
            "interpretation": self.interpretation,
        }


class V112DSidecarPilotAnalyzer:
    """Compare bounded black-box sidecars against the first interpretable baseline."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_dataset_payload: dict[str, Any],
        training_protocol_payload: dict[str, Any],
        baseline_readout_payload: dict[str, Any],
        sidecar_protocol_payload: dict[str, Any],
    ) -> V112DSidecarPilotReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_sidecar_pilot_next")):
            raise ValueError("V1.12D sidecar pilot requires an open V1.12D charter.")

        analyzer = V112BBaselineReadoutAnalyzer()
        client = TencentKlineClient()
        samples: list[TrainingSample] = []
        for row in list(pilot_dataset_payload.get("dataset_rows", [])):
            symbol = str(row.get("symbol"))
            bars = client.fetch_daily_bars(symbol).copy()
            samples.extend(
                analyzer._build_symbol_samples(  # noqa: SLF001
                    symbol=symbol,
                    cycle_window=dict(row.get("cycle_window", {})),
                    bars=bars,
                )
            )
        samples.sort(key=lambda item: item.trade_date)
        feature_names = list(analyzer.FEATURE_NAMES)
        classes = sorted(set(sample.label for sample in samples))
        label_to_int = {label: idx for idx, label in enumerate(classes)}

        x = np.array([[sample.feature_values[name] for name in feature_names] for sample in samples], dtype=float)
        y = np.array([label_to_int[sample.label] for sample in samples], dtype=int)
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))
        x_train, x_test = x[:split_index], x[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]
        test_samples = samples[split_index:]

        baseline_metrics = self._baseline_metrics(
            baseline_readout_payload=baseline_readout_payload,
            carry_class="carry_constructive",
        )
        carry_class_id = label_to_int["carry_constructive"]

        models = {
            "hist_gradient_boosting_classifier": HistGradientBoostingClassifier(
                max_depth=4,
                learning_rate=0.05,
                max_iter=150,
                random_state=42,
            ),
            "small_mlp_classifier": MLPClassifier(
                hidden_layer_sizes=(32, 16),
                activation="relu",
                alpha=1e-4,
                learning_rate_init=1e-3,
                max_iter=300,
                random_state=42,
            ),
        }

        model_rows: list[dict[str, Any]] = []
        for model_name, model in models.items():
            model.fit(x_train, y_train)
            preds = model.predict(x_test)
            model_rows.append(
                {
                    "model_name": model_name,
                    "test_accuracy": round(float(accuracy_score(y_test, preds)), 4),
                    "carry_constructive_precision": round(
                        float(precision_score(y_test, preds, labels=[carry_class_id], average="macro", zero_division=0)),
                        4,
                    ),
                    "carry_constructive_recall": round(
                        float(recall_score(y_test, preds, labels=[carry_class_id], average="macro", zero_division=0)),
                        4,
                    ),
                    "false_positive_count_in_major_markup": self._stage_false_positives(
                        test_samples=test_samples,
                        preds=preds,
                        predicted_class_id=carry_class_id,
                        true_class_id=carry_class_id,
                        target_stage="major_markup",
                    ),
                    "false_positive_count_in_high_level_consolidation": self._stage_false_positives(
                        test_samples=test_samples,
                        preds=preds,
                        predicted_class_id=carry_class_id,
                        true_class_id=carry_class_id,
                        target_stage="high_level_consolidation",
                    ),
                    "baseline_test_accuracy": baseline_metrics["test_accuracy"],
                    "baseline_false_positive_count_in_major_markup": baseline_metrics["major_markup_fp"],
                    "baseline_false_positive_count_in_high_level_consolidation": baseline_metrics["high_level_consolidation_fp"],
                    "same_dataset_rule_kept": True,
                    "same_time_split_rule_kept": True,
                }
            )

        best_model = max(model_rows, key=lambda row: row["test_accuracy"])
        summary = {
            "acceptance_posture": "freeze_v112d_first_same_dataset_sidecar_pilot_v1",
            "model_count": len(model_rows),
            "best_model_name": best_model["model_name"],
            "best_model_test_accuracy": best_model["test_accuracy"],
            "baseline_test_accuracy": baseline_metrics["test_accuracy"],
            "baseline_major_markup_fp": baseline_metrics["major_markup_fp"],
            "baseline_high_level_consolidation_fp": baseline_metrics["high_level_consolidation_fp"],
            "allow_strategy_training_now": False,
            "allow_sidecar_deployment_now": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "This is a same-dataset, same-label, same-split sidecar comparison, so differences are attributable to model family rather than scope drift.",
            "The comparison target is hotspot reduction, not generic leaderboard chasing.",
            "Even if a sidecar model improves hotspot behavior, the result remains report-only until a later review phase accepts it.",
        ]
        return V112DSidecarPilotReport(summary=summary, model_rows=model_rows, interpretation=interpretation)

    def _baseline_metrics(self, *, baseline_readout_payload: dict[str, Any], carry_class: str) -> dict[str, Any]:
        summary = dict(baseline_readout_payload.get("summary", {}))
        fold_rows = list(baseline_readout_payload.get("fold_rows", []))
        major_markup_fp = 0
        high_level_consolidation_fp = 0
        for row in fold_rows:
            if str(row.get("predicted_label")) == carry_class and str(row.get("true_label")) != carry_class:
                if str(row.get("stage")) == "major_markup":
                    major_markup_fp += 1
                if str(row.get("stage")) == "high_level_consolidation":
                    high_level_consolidation_fp += 1
        return {
            "test_accuracy": float(summary.get("test_accuracy", 0.0)),
            "major_markup_fp": major_markup_fp,
            "high_level_consolidation_fp": high_level_consolidation_fp,
        }

    def _stage_false_positives(
        self,
        *,
        test_samples: list[TrainingSample],
        preds: np.ndarray,
        predicted_class_id: int,
        true_class_id: int,
        target_stage: str,
    ) -> int:
        total = 0
        for idx, sample in enumerate(test_samples):
            if sample.stage != target_stage:
                continue
            if int(preds[idx]) == predicted_class_id and sample.label != "carry_constructive":
                total += 1
        return total


def write_v112d_sidecar_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112DSidecarPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
