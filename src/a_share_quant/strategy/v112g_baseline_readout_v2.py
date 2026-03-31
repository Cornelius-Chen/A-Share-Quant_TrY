from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient
from a_share_quant.strategy.v112b_baseline_readout_v1 import TrainingSample, V112BBaselineReadoutAnalyzer


@dataclass(slots=True)
class V112GBaselineReadoutV2Report:
    summary: dict[str, Any]
    feature_names: list[str]
    fold_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_names": self.feature_names,
            "fold_rows": self.fold_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112GBaselineReadoutV2Analyzer:
    BASE_FEATURE_NAMES = list(V112BBaselineReadoutAnalyzer.FEATURE_NAMES)
    NEW_FEATURE_NAMES = ["catalyst_freshness_state", "cross_day_catalyst_persistence", "theme_breadth_confirmation_proxy"]
    FEATURE_NAMES = BASE_FEATURE_NAMES + NEW_FEATURE_NAMES

    def build_augmented_samples(
        self,
        *,
        pilot_dataset_payload: dict[str, Any],
        bar_frames_by_symbol: dict[str, pd.DataFrame] | None = None,
    ) -> list[TrainingSample]:
        base_analyzer = V112BBaselineReadoutAnalyzer()
        client = TencentKlineClient()
        sample_rows: list[TrainingSample] = []
        for row in list(pilot_dataset_payload.get("dataset_rows", [])):
            symbol = str(row.get("symbol"))
            bars = (
                bar_frames_by_symbol[symbol].copy()
                if bar_frames_by_symbol and symbol in bar_frames_by_symbol
                else client.fetch_daily_bars(symbol).copy()
            )
            sample_rows.extend(
                base_analyzer._build_symbol_samples(  # noqa: SLF001
                    symbol=symbol,
                    cycle_window=dict(row.get("cycle_window", {})),
                    bars=bars,
                )
            )
        sample_rows.sort(key=lambda item: item.trade_date)
        breadth_by_date = self._cohort_breadth(sample_rows)

        augmented_rows: list[TrainingSample] = []
        for sample in sample_rows:
            base = dict(sample.feature_values)
            catalyst_presence = float(base["official_or_industry_catalyst_presence"])
            demand_accel = float(base["demand_acceleration_proxy"])
            price_change = float(base["product_price_change_proxy"])
            rel_strength = float(base["relative_strength_persistence"])
            breakout_hold = float(base["breakout_or_hold_structure"])

            freshness = max(0.0, demand_accel) * (1.0 + catalyst_presence) + 0.15 * breakout_hold
            persistence = max(0.0, price_change) * catalyst_presence + max(0.0, rel_strength)
            breadth = float(breadth_by_date.get(sample.trade_date, 0.0)) * (0.5 + catalyst_presence)

            base["catalyst_freshness_state"] = round(float(freshness), 6)
            base["cross_day_catalyst_persistence"] = round(float(persistence), 6)
            base["theme_breadth_confirmation_proxy"] = round(float(breadth), 6)
            augmented_rows.append(
                TrainingSample(
                    trade_date=sample.trade_date,
                    symbol=sample.symbol,
                    stage=sample.stage,
                    label=sample.label,
                    feature_values=base,
                    forward_return_20d=sample.forward_return_20d,
                    max_drawdown_20d=sample.max_drawdown_20d,
                    forward_return_bucket=sample.forward_return_bucket,
                    max_drawdown_bucket=sample.max_drawdown_bucket,
                )
            )
        return augmented_rows

    def analyze(
        self,
        *,
        pilot_dataset_payload: dict[str, Any],
        training_protocol_payload: dict[str, Any],
        baseline_v1_payload: dict[str, Any],
        bar_frames_by_symbol: dict[str, pd.DataFrame] | None = None,
    ) -> V112GBaselineReadoutV2Report:
        protocol_summary = dict(training_protocol_payload.get("summary", {}))
        if str(protocol_summary.get("acceptance_posture")) != "freeze_v112_training_protocol_v1":
            raise ValueError("V1.12G baseline rerun requires the frozen V1.12 protocol.")

        samples = self.build_augmented_samples(
            pilot_dataset_payload=pilot_dataset_payload,
            bar_frames_by_symbol=bar_frames_by_symbol,
        )
        feature_matrix = np.array([[sample.feature_values[name] for name in self.FEATURE_NAMES] for sample in samples], dtype=float)
        labels = [sample.label for sample in samples]
        classes = sorted(set(labels))
        label_ids = np.array([classes.index(label) for label in labels], dtype=int)
        order = np.argsort([sample.trade_date for sample in samples])
        feature_matrix = feature_matrix[order]
        label_ids = label_ids[order]
        ordered_samples = [samples[int(idx)] for idx in order]
        split_index = max(1, min(len(ordered_samples) - 1, int(len(ordered_samples) * 0.7)))
        x_train = feature_matrix[:split_index]
        y_train = label_ids[:split_index]
        x_test = feature_matrix[split_index:]
        y_test = label_ids[split_index:]
        ordered_test_samples = ordered_samples[split_index:]

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

        fold_rows: list[dict[str, Any]] = []
        for idx, sample in enumerate(ordered_test_samples):
            distances = np.linalg.norm(centroid_matrix - x_test_scaled[idx], axis=1)
            pred_class = int(centroid_classes[int(np.argmin(distances))])
            true_class = int(y_test[idx])
            fold_rows.append(
                {
                    "trade_date": sample.trade_date,
                    "symbol": sample.symbol,
                    "stage": sample.stage,
                    "predicted_label": classes[pred_class],
                    "true_label": classes[true_class],
                    "correct": pred_class == true_class,
                }
            )

        test_accuracy = sum(1 for row in fold_rows if bool(row["correct"])) / len(fold_rows)
        baseline_v1_summary = dict(baseline_v1_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "freeze_v112g_baseline_readout_v2",
            "feature_count_v2": len(self.FEATURE_NAMES),
            "baseline_v1_test_accuracy": float(baseline_v1_summary.get("test_accuracy", 0.0)),
            "baseline_v2_test_accuracy": round(float(test_accuracy), 4),
            "baseline_v1_major_markup_fp": self._stage_false_positive_count(fold_rows=list(baseline_v1_payload.get("fold_rows", [])), target_stage="major_markup"),
            "baseline_v1_high_level_consolidation_fp": self._stage_false_positive_count(fold_rows=list(baseline_v1_payload.get("fold_rows", [])), target_stage="high_level_consolidation"),
            "baseline_v2_major_markup_fp": self._stage_false_positive_count(fold_rows=fold_rows, target_stage="major_markup"),
            "baseline_v2_high_level_consolidation_fp": self._stage_false_positive_count(fold_rows=fold_rows, target_stage="high_level_consolidation"),
            "ready_for_gbdt_v2_next": True,
        }
        interpretation = [
            "This rerun keeps the same dataset and labels but upgrades catalyst-state representation.",
            "The question is whether richer state semantics help the simple baseline before any new model-family escalation.",
            "The most important comparison remains hotspot false positives, not generic score chasing.",
        ]
        return V112GBaselineReadoutV2Report(summary=summary, feature_names=self.FEATURE_NAMES, fold_rows=fold_rows, interpretation=interpretation)

    def _cohort_breadth(self, sample_rows: list[TrainingSample]) -> dict[str, float]:
        grouped: dict[str, list[TrainingSample]] = {}
        for sample in sample_rows:
            grouped.setdefault(sample.trade_date, []).append(sample)
        breadth_by_date: dict[str, float] = {}
        for trade_date, rows in grouped.items():
            positive = 0
            for sample in rows:
                rel_strength = float(sample.feature_values["relative_strength_persistence"])
                demand_accel = float(sample.feature_values["demand_acceleration_proxy"])
                if rel_strength > 0.0 and demand_accel > -0.02:
                    positive += 1
            breadth_by_date[trade_date] = positive / len(rows) if rows else 0.0
        return breadth_by_date

    def _stage_false_positive_count(self, *, fold_rows: list[dict[str, Any]], target_stage: str) -> int:
        total = 0
        for row in fold_rows:
            if str(row.get("stage")) != target_stage:
                continue
            if str(row.get("predicted_label")) == "carry_constructive" and str(row.get("true_label")) != "carry_constructive":
                total += 1
        return total


def write_v112g_baseline_readout_v2_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112GBaselineReadoutV2Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
