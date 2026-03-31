from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

from a_share_quant.strategy.v112g_baseline_readout_v2 import V112GBaselineReadoutV2Analyzer, load_json_report
from a_share_quant.strategy.v112h_candidate_substate_clustering_v1 import V112HCandidateSubstateClusteringAnalyzer


@dataclass(slots=True)
class V112NShadowRerunReport:
    summary: dict[str, Any]
    shadow_feature_rows: list[dict[str, Any]]
    model_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "shadow_feature_rows": self.shadow_feature_rows,
            "model_rows": self.model_rows,
            "interpretation": self.interpretation,
        }


class V112NShadowRerunAnalyzer:
    SHADOW_FEATURES = [
        "shadow_quiet_contraction_stall_recoverable",
        "shadow_residual_breadth_stall_exhaustion",
        "shadow_unresolved_mixed_stall_residue",
    ]

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_dataset_payload: dict[str, Any],
        baseline_v2_payload: dict[str, Any],
        gbdt_v2_payload: dict[str, Any],
    ) -> V112NShadowRerunReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_shadow_rerun_next")):
            raise ValueError("V1.12N requires an open shadow-rerun charter.")

        analyzer = V112GBaselineReadoutV2Analyzer()
        cluster_analyzer = V112HCandidateSubstateClusteringAnalyzer()
        samples = analyzer.build_augmented_samples(pilot_dataset_payload=pilot_dataset_payload)
        for sample in samples:
            self._attach_shadow_flags(sample=sample, cluster_analyzer=cluster_analyzer)
        samples.sort(key=lambda item: item.trade_date)

        feature_names = list(analyzer.FEATURE_NAMES) + list(self.SHADOW_FEATURES)
        classes = sorted(set(sample.label for sample in samples))
        label_to_int = {label: idx for idx, label in enumerate(classes)}
        x = np.array([[sample.feature_values[name] for name in feature_names] for sample in samples], dtype=float)
        y = np.array([label_to_int[sample.label] for sample in samples], dtype=int)
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))
        x_train, x_test = x[:split_index], x[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]
        test_samples = samples[split_index:]

        baseline_preds = self._predict_nearest_centroid(x_train=x_train, y_train=y_train, x_test=x_test)
        gbdt_model = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=150, random_state=42)
        gbdt_model.fit(x_train, y_train)
        gbdt_preds = np.asarray(gbdt_model.predict(x_test), dtype=int)

        carry_class_id = label_to_int["carry_constructive"]
        baseline_v2_summary = dict(baseline_v2_payload.get("summary", {}))
        gbdt_v2_summary = dict(gbdt_v2_payload.get("summary", {}))

        model_rows = [
            {
                "model_name": "baseline_shadow_v1",
                "test_accuracy": round(float((baseline_preds == y_test).mean()), 4),
                "prior_test_accuracy": float(baseline_v2_summary.get("baseline_v2_test_accuracy", 0.0)),
                "high_level_consolidation_carry_fp": self._stage_false_positives(
                    test_samples=test_samples,
                    preds=baseline_preds,
                    carry_class_id=carry_class_id,
                    target_stage="high_level_consolidation",
                ),
                "prior_high_level_consolidation_carry_fp": int(
                    baseline_v2_summary.get("baseline_v2_high_level_consolidation_fp", 0)
                ),
                "major_markup_carry_fp": self._stage_false_positives(
                    test_samples=test_samples,
                    preds=baseline_preds,
                    carry_class_id=carry_class_id,
                    target_stage="major_markup",
                ),
                "prior_major_markup_carry_fp": int(baseline_v2_summary.get("baseline_v2_major_markup_fp", 0)),
            },
            {
                "model_name": "gbdt_shadow_v1",
                "test_accuracy": round(float((gbdt_preds == y_test).mean()), 4),
                "prior_test_accuracy": float(gbdt_v2_summary.get("gbdt_v2_test_accuracy", 0.0)),
                "high_level_consolidation_carry_fp": self._stage_false_positives(
                    test_samples=test_samples,
                    preds=gbdt_preds,
                    carry_class_id=carry_class_id,
                    target_stage="high_level_consolidation",
                ),
                "prior_high_level_consolidation_carry_fp": int(gbdt_v2_summary.get("gbdt_v2_high_level_consolidation_fp", 0)),
                "major_markup_carry_fp": self._stage_false_positives(
                    test_samples=test_samples,
                    preds=gbdt_preds,
                    carry_class_id=carry_class_id,
                    target_stage="major_markup",
                ),
                "prior_major_markup_carry_fp": int(gbdt_v2_summary.get("gbdt_v2_major_markup_fp", 0)),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112n_shadow_rerun_v1",
            "shadow_feature_count": len(self.SHADOW_FEATURES),
            "baseline_shadow_test_accuracy": model_rows[0]["test_accuracy"],
            "baseline_v2_test_accuracy": model_rows[0]["prior_test_accuracy"],
            "gbdt_shadow_test_accuracy": model_rows[1]["test_accuracy"],
            "gbdt_v2_test_accuracy": model_rows[1]["prior_test_accuracy"],
            "baseline_shadow_incremental_gain_present": model_rows[0]["test_accuracy"] > model_rows[0]["prior_test_accuracy"],
            "gbdt_shadow_incremental_gain_present": model_rows[1]["test_accuracy"] > model_rows[1]["prior_test_accuracy"],
            "ready_for_phase_check_next": True,
        }
        shadow_feature_rows = [
            {
                "feature_name": "shadow_quiet_contraction_stall_recoverable",
                "source_reading": "quiet contraction inside mixed stall cluster",
            },
            {
                "feature_name": "shadow_residual_breadth_stall_exhaustion",
                "source_reading": "residual breadth with exhaustion tendency",
            },
            {
                "feature_name": "shadow_unresolved_mixed_stall_residue",
                "source_reading": "remaining unresolved mixed residue after one inner pass",
            },
        ]
        interpretation = [
            "The shadow rerun keeps the same dataset, same labels, and same split; only review-only inner-draft flags are added.",
            "If metrics do not move, the result still matters: it means the inner draft is currently more descriptive than incrementally predictive.",
            "No formal schema change is authorized from this rerun.",
        ]
        return V112NShadowRerunReport(
            summary=summary,
            shadow_feature_rows=shadow_feature_rows,
            model_rows=model_rows,
            interpretation=interpretation,
        )

    def _attach_shadow_flags(self, *, sample, cluster_analyzer: V112HCandidateSubstateClusteringAnalyzer) -> None:
        feature_values = sample.feature_values
        quiet = residual = unresolved = 0.0
        if sample.stage == "high_level_consolidation" and cluster_analyzer._cluster_name(sample) == "breadth_thin_catalyst_stale":
            breadth = float(feature_values["theme_breadth_confirmation_proxy"])
            price_change = float(feature_values["product_price_change_proxy"])
            rel_strength = float(feature_values["relative_strength_persistence"])
            vol_ratio = float(feature_values["volume_expansion_confirmation"])
            if breadth >= 0.333333 and price_change <= 0.0:
                residual = 1.0
            elif breadth < 0.333333 and price_change <= 0.0 and rel_strength <= 0.0 and vol_ratio < 1.0:
                quiet = 1.0
            else:
                unresolved = 1.0
        feature_values["shadow_quiet_contraction_stall_recoverable"] = quiet
        feature_values["shadow_residual_breadth_stall_exhaustion"] = residual
        feature_values["shadow_unresolved_mixed_stall_residue"] = unresolved

    def _predict_nearest_centroid(self, *, x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> np.ndarray:
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
        preds = []
        for row in x_test_scaled:
            distances = np.linalg.norm(centroid_matrix - row, axis=1)
            preds.append(int(centroid_classes[int(np.argmin(distances))]))
        return np.array(preds, dtype=int)

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


def write_v112n_shadow_rerun_report(*, reports_dir: Path, report_name: str, result: V112NShadowRerunReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
