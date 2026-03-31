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

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient
from a_share_quant.strategy.v112b_baseline_readout_v1 import (
    TrainingSample,
    V112BBaselineReadoutAnalyzer,
)


@dataclass(slots=True)
class V112EGBDTAttributionReviewReport:
    summary: dict[str, Any]
    base_model_row: dict[str, Any]
    block_ablation_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "base_model_row": self.base_model_row,
            "block_ablation_rows": self.block_ablation_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112EGBDTAttributionReviewAnalyzer:
    """Explain the first GBDT sidecar gain with block ablation."""

    FEATURE_BLOCKS = {
        "catalyst_state": [
            "product_price_change_proxy",
            "demand_acceleration_proxy",
            "supply_tightness_proxy",
            "official_or_industry_catalyst_presence",
        ],
        "earnings_transmission_bridge": [
            "revenue_sensitivity_class",
            "gross_margin_sensitivity_class",
            "order_or_capacity_sensitivity_proxy",
        ],
        "expectation_gap": [
            "earnings_revision_pressure_proxy",
            "rerating_gap_proxy",
        ],
        "price_confirmation": [
            "relative_strength_persistence",
            "volume_expansion_confirmation",
            "breakout_or_hold_structure",
        ],
    }

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_dataset_payload: dict[str, Any],
        baseline_readout_payload: dict[str, Any],
    ) -> V112EGBDTAttributionReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_attribution_review_next")):
            raise ValueError("V1.12E attribution review requires an open V1.12E charter.")

        samples = self._load_samples(pilot_dataset_payload=pilot_dataset_payload)
        feature_names = list(V112BBaselineReadoutAnalyzer.FEATURE_NAMES)
        x = np.array([[sample.feature_values[name] for name in feature_names] for sample in samples], dtype=float)
        labels = sorted(set(sample.label for sample in samples))
        label_to_id = {label: idx for idx, label in enumerate(labels)}
        y = np.array([label_to_id[sample.label] for sample in samples], dtype=int)
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))
        x_train, x_test = x[:split_index], x[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]
        test_samples = samples[split_index:]

        baseline_metrics = self._baseline_metrics(baseline_readout_payload=baseline_readout_payload)
        base_model_row = self._fit_and_score(
            model_name="hist_gradient_boosting_classifier",
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
            test_samples=test_samples,
            carry_class_id=label_to_id["carry_constructive"],
        )

        block_ablation_rows: list[dict[str, Any]] = []
        for block_name, block_features in self.FEATURE_BLOCKS.items():
            keep_idx = [idx for idx, name in enumerate(feature_names) if name not in block_features]
            ablation_row = self._fit_and_score(
                model_name=f"hist_gradient_boosting_minus_{block_name}",
                x_train=x_train[:, keep_idx],
                y_train=y_train,
                x_test=x_test[:, keep_idx],
                y_test=y_test,
                test_samples=test_samples,
                carry_class_id=label_to_id["carry_constructive"],
            )
            ablation_row["ablated_block"] = block_name
            ablation_row["removed_feature_count"] = len(block_features)
            ablation_row["accuracy_delta_vs_full"] = round(
                ablation_row["test_accuracy"] - base_model_row["test_accuracy"], 4
            )
            ablation_row["major_markup_fp_delta_vs_full"] = (
                ablation_row["false_positive_count_in_major_markup"]
                - base_model_row["false_positive_count_in_major_markup"]
            )
            ablation_row["high_level_consolidation_fp_delta_vs_full"] = (
                ablation_row["false_positive_count_in_high_level_consolidation"]
                - base_model_row["false_positive_count_in_high_level_consolidation"]
            )
            block_ablation_rows.append(ablation_row)

        most_useful_block = max(
            block_ablation_rows,
            key=lambda row: (
                row["major_markup_fp_delta_vs_full"] + row["high_level_consolidation_fp_delta_vs_full"],
                -row["accuracy_delta_vs_full"],
            ),
        )
        summary = {
            "acceptance_posture": "freeze_v112e_gbdt_attribution_review_v1",
            "block_count": len(block_ablation_rows),
            "full_model_test_accuracy": base_model_row["test_accuracy"],
            "baseline_test_accuracy": baseline_metrics["baseline_test_accuracy"],
            "most_useful_block_by_hotspot_impact": most_useful_block["ablated_block"],
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "This review explains the first GBDT gain by removing one feature block at a time under the same dataset and split.",
            "The most useful block is the one whose removal hurts hotspot false-positive control the most.",
            "This should inform whether the next move is feature refinement, label refinement, or further sidecar comparison.",
        ]
        return V112EGBDTAttributionReviewReport(
            summary=summary,
            base_model_row={**base_model_row, **baseline_metrics},
            block_ablation_rows=block_ablation_rows,
            interpretation=interpretation,
        )

    def _load_samples(self, *, pilot_dataset_payload: dict[str, Any]) -> list[TrainingSample]:
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
        return samples

    def _fit_and_score(
        self,
        *,
        model_name: str,
        x_train: np.ndarray,
        y_train: np.ndarray,
        x_test: np.ndarray,
        y_test: np.ndarray,
        test_samples: list[TrainingSample],
        carry_class_id: int,
    ) -> dict[str, Any]:
        model = HistGradientBoostingClassifier(
            max_depth=4,
            learning_rate=0.05,
            max_iter=150,
            random_state=42,
        )
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
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
            "false_positive_count_in_major_markup": self._stage_false_positives(
                test_samples=test_samples,
                preds=preds,
                predicted_class_id=carry_class_id,
                target_stage="major_markup",
            ),
            "false_positive_count_in_high_level_consolidation": self._stage_false_positives(
                test_samples=test_samples,
                preds=preds,
                predicted_class_id=carry_class_id,
                target_stage="high_level_consolidation",
            ),
        }

    def _baseline_metrics(self, *, baseline_readout_payload: dict[str, Any]) -> dict[str, Any]:
        summary = dict(baseline_readout_payload.get("summary", {}))
        fold_rows = list(baseline_readout_payload.get("fold_rows", []))
        major_markup_fp = 0
        high_level_consolidation_fp = 0
        for row in fold_rows:
            if str(row.get("predicted_label")) == "carry_constructive" and str(row.get("true_label")) != "carry_constructive":
                if str(row.get("stage")) == "major_markup":
                    major_markup_fp += 1
                if str(row.get("stage")) == "high_level_consolidation":
                    high_level_consolidation_fp += 1
        return {
            "baseline_test_accuracy": float(summary.get("test_accuracy", 0.0)),
            "baseline_major_markup_fp": major_markup_fp,
            "baseline_high_level_consolidation_fp": high_level_consolidation_fp,
        }

    def _stage_false_positives(
        self,
        *,
        test_samples: list[TrainingSample],
        preds: np.ndarray,
        predicted_class_id: int,
        target_stage: str,
    ) -> int:
        total = 0
        for idx, sample in enumerate(test_samples):
            if sample.stage != target_stage:
                continue
            if int(preds[idx]) == predicted_class_id and sample.label != "carry_constructive":
                total += 1
        return total


def write_v112e_gbdt_attribution_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112EGBDTAttributionReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
