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

from a_share_quant.strategy.v112g_baseline_readout_v2 import V112GBaselineReadoutV2Analyzer


@dataclass(slots=True)
class V112GGBDTPilotV2Report:
    summary: dict[str, Any]
    model_row: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "model_row": self.model_row,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112GGBDTPilotV2Analyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_dataset_payload: dict[str, Any],
        baseline_v1_payload: dict[str, Any],
        gbdt_v1_payload: dict[str, Any],
        baseline_v2_payload: dict[str, Any],
    ) -> V112GGBDTPilotV2Report:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_feature_schema_v2_next")):
            raise ValueError("V1.12G GBDT rerun requires an open V1.12G charter.")

        analyzer = V112GBaselineReadoutV2Analyzer()
        samples = analyzer.build_augmented_samples(pilot_dataset_payload=pilot_dataset_payload)
        feature_names = list(analyzer.FEATURE_NAMES)
        classes = sorted(set(sample.label for sample in samples))
        label_to_int = {label: idx for idx, label in enumerate(classes)}
        x = np.array([[sample.feature_values[name] for name in feature_names] for sample in samples], dtype=float)
        y = np.array([label_to_int[sample.label] for sample in samples], dtype=int)
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))
        x_train, x_test = x[:split_index], x[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]
        test_samples = samples[split_index:]
        carry_class_id = label_to_int["carry_constructive"]

        model = HistGradientBoostingClassifier(
            max_depth=4,
            learning_rate=0.05,
            max_iter=150,
            random_state=42,
        )
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        model_row = {
            "model_name": "hist_gradient_boosting_classifier_v2",
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
                test_samples=test_samples, preds=preds, carry_class_id=carry_class_id, target_stage="major_markup"
            ),
            "false_positive_count_in_high_level_consolidation": self._stage_false_positives(
                test_samples=test_samples, preds=preds, carry_class_id=carry_class_id, target_stage="high_level_consolidation"
            ),
        }

        gbdt_v1_row = next(
            row for row in list(gbdt_v1_payload.get("model_rows", []))
            if str(row.get("model_name")) == "hist_gradient_boosting_classifier"
        )
        baseline_v1_summary = dict(baseline_v1_payload.get("summary", {}))
        baseline_v2_summary = dict(baseline_v2_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "freeze_v112g_gbdt_pilot_v2",
            "baseline_v1_test_accuracy": float(baseline_v1_summary.get("test_accuracy", 0.0)),
            "baseline_v2_test_accuracy": float(baseline_v2_summary.get("baseline_v2_test_accuracy", 0.0)),
            "gbdt_v1_test_accuracy": float(gbdt_v1_row.get("test_accuracy", 0.0)),
            "gbdt_v2_test_accuracy": model_row["test_accuracy"],
            "gbdt_v1_major_markup_fp": int(gbdt_v1_row.get("false_positive_count_in_major_markup", 0)),
            "gbdt_v2_major_markup_fp": model_row["false_positive_count_in_major_markup"],
            "gbdt_v1_high_level_consolidation_fp": int(gbdt_v1_row.get("false_positive_count_in_high_level_consolidation", 0)),
            "gbdt_v2_high_level_consolidation_fp": model_row["false_positive_count_in_high_level_consolidation"],
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "This rerun keeps the same frozen dataset and same GBDT family; only catalyst-state representation changes.",
            "The highest-value comparison is whether hotspot optimism improves without paying too much elsewhere.",
            "The result should inform whether to implement feature v2, label refinement, or both.",
        ]
        return V112GGBDTPilotV2Report(summary=summary, model_row=model_row, interpretation=interpretation)

    def _stage_false_positives(
        self,
        *,
        test_samples: list[Any],
        preds: np.ndarray,
        carry_class_id: int,
        target_stage: str,
    ) -> int:
        total = 0
        for idx, sample in enumerate(test_samples):
            if sample.stage != target_stage:
                continue
            if int(preds[idx]) == carry_class_id and sample.label != "carry_constructive":
                total += 1
        return total


def write_v112g_gbdt_pilot_v2_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112GGBDTPilotV2Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
