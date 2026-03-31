from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.neural_network import MLPClassifier

from a_share_quant.strategy.v112b_baseline_readout_v1 import TrainingSample
from a_share_quant.strategy.v112g_baseline_readout_v2 import V112GBaselineReadoutV2Analyzer


@dataclass(slots=True)
class V112ZModelPayoffProbeReport:
    summary: dict[str, Any]
    model_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "model_rows": self.model_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ZModelPayoffProbeAnalyzer:
    HOLDING_DAYS = 20

    def analyze(
        self,
        *,
        operational_charter_payload: dict[str, Any],
        pilot_dataset_payload: dict[str, Any],
    ) -> V112ZModelPayoffProbeReport:
        charter_summary = dict(operational_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_reconstruction_pass")):
            raise ValueError("The V1.12Z operational charter must be frozen before the payoff probe runs.")

        analyzer = V112GBaselineReadoutV2Analyzer()
        samples = analyzer.build_augmented_samples(pilot_dataset_payload=pilot_dataset_payload)
        samples.sort(key=lambda item: item.trade_date)

        feature_names = list(analyzer.FEATURE_NAMES)
        classes = sorted(set(sample.label for sample in samples))
        label_to_int = {label: idx for idx, label in enumerate(classes)}
        carry_class_id = label_to_int["carry_constructive"]

        x = np.array([[sample.feature_values[name] for name in feature_names] for sample in samples], dtype=float)
        y = np.array([label_to_int[sample.label] for sample in samples], dtype=int)
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))
        x_train, x_test = x[:split_index], x[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]
        test_samples = samples[split_index:]

        model_rows: list[dict[str, Any]] = []

        baseline_preds = self._nearest_centroid_predictions(x_train=x_train, y_train=y_train, x_test=x_test)
        model_rows.append(
            self._model_row(
                model_name="guardrail_nearest_centroid_v2",
                preds=baseline_preds,
                y_test=y_test,
                test_samples=test_samples,
                carry_class_id=carry_class_id,
            )
        )

        gbdt = HistGradientBoostingClassifier(
            max_depth=4,
            learning_rate=0.05,
            max_iter=150,
            random_state=42,
        )
        gbdt.fit(x_train, y_train)
        gbdt_preds = gbdt.predict(x_test)
        model_rows.append(
            self._model_row(
                model_name="hist_gradient_boosting_classifier_v2",
                preds=gbdt_preds,
                y_test=y_test,
                test_samples=test_samples,
                carry_class_id=carry_class_id,
            )
        )

        mlp = MLPClassifier(
            hidden_layer_sizes=(32, 16),
            activation="relu",
            alpha=1e-4,
            learning_rate_init=1e-3,
            max_iter=300,
            random_state=42,
        )
        mlp.fit(x_train, y_train)
        mlp_preds = mlp.predict(x_test)
        model_rows.append(
            self._model_row(
                model_name="small_mlp_classifier_v2",
                preds=mlp_preds,
                y_test=y_test,
                test_samples=test_samples,
                carry_class_id=carry_class_id,
            )
        )

        best_by_payoff = max(model_rows, key=lambda row: float(row["non_overlap_trade_probe"]["profit_factor"]))
        summary = {
            "acceptance_posture": "freeze_v112z_report_only_model_payoff_probe_v1",
            "sample_count": len(samples),
            "train_count": int(split_index),
            "test_count": int(len(samples) - split_index),
            "model_count": len(model_rows),
            "primary_positive_label": "carry_constructive",
            "holding_days_for_probe": self.HOLDING_DAYS,
            "best_model_by_profit_factor": best_by_payoff["model_name"],
            "best_model_profit_factor": best_by_payoff["non_overlap_trade_probe"]["profit_factor"],
            "formal_training_still_forbidden": True,
            "execution_still_forbidden": True,
            "ready_for_owner_review_next": True,
        }
        interpretation = [
            "This is a report-only payoff probe on the frozen optical-link pilot, not a live-trading backtest.",
            "All models use the same time split and the same dataset so payoff differences remain attributable to model family rather than scope drift.",
            "The non-overlap trade probe is a bounded approximation of trade quality, meant to compare cycle absorption quality before any formal training rights are opened.",
        ]
        return V112ZModelPayoffProbeReport(summary=summary, model_rows=model_rows, interpretation=interpretation)

    def _nearest_centroid_predictions(self, *, x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> np.ndarray:
        mean = x_train.mean(axis=0)
        std = x_train.std(axis=0)
        std[std == 0.0] = 1.0
        x_train_scaled = (x_train - mean) / std
        x_test_scaled = (x_test - mean) / std
        centroids = []
        centroid_classes = []
        for class_id in sorted(set(int(value) for value in y_train)):
            centroids.append(x_train_scaled[y_train == class_id].mean(axis=0))
            centroid_classes.append(class_id)
        centroid_matrix = np.vstack(centroids)
        preds: list[int] = []
        for idx in range(len(x_test_scaled)):
            distances = np.linalg.norm(centroid_matrix - x_test_scaled[idx], axis=1)
            preds.append(int(centroid_classes[int(np.argmin(distances))]))
        return np.array(preds, dtype=int)

    def _model_row(
        self,
        *,
        model_name: str,
        preds: np.ndarray,
        y_test: np.ndarray,
        test_samples: list[TrainingSample],
        carry_class_id: int,
    ) -> dict[str, Any]:
        conditional_payoff = self._conditional_payoff(
            preds=preds,
            test_samples=test_samples,
            carry_class_id=carry_class_id,
        )
        non_overlap_probe = self._non_overlap_trade_probe(
            preds=preds,
            test_samples=test_samples,
            carry_class_id=carry_class_id,
        )
        return {
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
            "conditional_carry_payoff": conditional_payoff,
            "non_overlap_trade_probe": non_overlap_probe,
        }

    def _conditional_payoff(
        self,
        *,
        preds: np.ndarray,
        test_samples: list[TrainingSample],
        carry_class_id: int,
    ) -> dict[str, Any]:
        chosen = [
            sample.forward_return_20d
            for idx, sample in enumerate(test_samples)
            if int(preds[idx]) == carry_class_id
        ]
        chosen_drawdowns = [
            sample.max_drawdown_20d
            for idx, sample in enumerate(test_samples)
            if int(preds[idx]) == carry_class_id
        ]
        return self._payoff_stats(
            forward_returns=chosen,
            max_drawdowns=chosen_drawdowns,
        )

    def _non_overlap_trade_probe(
        self,
        *,
        preds: np.ndarray,
        test_samples: list[TrainingSample],
        carry_class_id: int,
    ) -> dict[str, Any]:
        accepted_returns: list[float] = []
        accepted_drawdowns: list[float] = []
        last_taken_index_by_symbol: dict[str, int] = {}
        local_index_by_symbol: dict[str, int] = {}

        for idx, sample in enumerate(test_samples):
            local_index = local_index_by_symbol.get(sample.symbol, 0)
            local_index_by_symbol[sample.symbol] = local_index + 1
            if int(preds[idx]) != carry_class_id:
                continue
            last_taken = last_taken_index_by_symbol.get(sample.symbol)
            if last_taken is not None and local_index - last_taken < self.HOLDING_DAYS:
                continue
            last_taken_index_by_symbol[sample.symbol] = local_index
            accepted_returns.append(sample.forward_return_20d)
            accepted_drawdowns.append(sample.max_drawdown_20d)

        return self._payoff_stats(
            forward_returns=accepted_returns,
            max_drawdowns=accepted_drawdowns,
        )

    def _payoff_stats(self, *, forward_returns: list[float], max_drawdowns: list[float]) -> dict[str, Any]:
        if not forward_returns:
            return {
                "trade_count": 0,
                "avg_forward_return_20d": 0.0,
                "median_forward_return_20d": 0.0,
                "hit_rate": 0.0,
                "avg_max_drawdown_20d": 0.0,
                "profit_factor": 0.0,
                "return_over_drawdown": 0.0,
            }

        positive_sum = sum(value for value in forward_returns if value > 0.0)
        negative_sum = sum(value for value in forward_returns if value < 0.0)
        profit_factor = positive_sum / abs(negative_sum) if negative_sum < 0.0 else float("inf")
        avg_return = sum(forward_returns) / len(forward_returns)
        avg_drawdown = sum(max_drawdowns) / len(max_drawdowns) if max_drawdowns else 0.0
        hit_rate = sum(1 for value in forward_returns if value > 0.0) / len(forward_returns)
        return {
            "trade_count": len(forward_returns),
            "avg_forward_return_20d": round(float(avg_return), 4),
            "median_forward_return_20d": round(float(median(forward_returns)), 4),
            "hit_rate": round(float(hit_rate), 4),
            "avg_max_drawdown_20d": round(float(avg_drawdown), 4),
            "profit_factor": round(float(profit_factor), 4) if profit_factor != float("inf") else "inf",
            "return_over_drawdown": round(float(avg_return / abs(avg_drawdown)), 4) if avg_drawdown < 0.0 else "inf",
        }


def write_v112z_model_payoff_probe_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ZModelPayoffProbeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
