from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

from a_share_quant.strategy.v112b_baseline_readout_v1 import TrainingSample
from a_share_quant.strategy.v112g_baseline_readout_v2 import V112GBaselineReadoutV2Analyzer


@dataclass(slots=True)
class V112HCandidateSubstateClusteringReport:
    summary: dict[str, Any]
    cluster_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "cluster_rows": self.cluster_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112HCandidateSubstateClusteringAnalyzer:
    CLUSTER_FEATURE_NAMES = [
        "theme_breadth_confirmation_proxy",
        "catalyst_freshness_state",
        "cross_day_catalyst_persistence",
        "product_price_change_proxy",
        "demand_acceleration_proxy",
        "relative_strength_persistence",
        "volume_expansion_confirmation",
        "breakout_or_hold_structure",
    ]

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_dataset_payload: dict[str, Any],
        training_protocol_payload: dict[str, Any],
        baseline_v2_payload: dict[str, Any],
        gbdt_v2_payload: dict[str, Any],
    ) -> V112HCandidateSubstateClusteringReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_candidate_substate_draft_next")):
            raise ValueError("V1.12H requires an open V1.12H charter.")

        analyzer = V112GBaselineReadoutV2Analyzer()
        samples = [
            sample
            for sample in analyzer.build_augmented_samples(pilot_dataset_payload=pilot_dataset_payload)
            if sample.stage == "high_level_consolidation"
        ]
        if not samples:
            raise ValueError("V1.12H requires high_level_consolidation samples from the frozen pilot dataset.")
        baseline_v2_summary = dict(baseline_v2_payload.get("summary", {}))
        gbdt_v2_summary = dict(gbdt_v2_payload.get("summary", {}))
        return self._build_from_samples(
            samples=samples,
            baseline_summary=baseline_v2_summary,
            gbdt_summary=gbdt_v2_summary,
        )

    def _build_from_samples(
        self,
        *,
        samples: list[TrainingSample],
        baseline_summary: dict[str, Any],
        gbdt_summary: dict[str, Any],
    ) -> V112HCandidateSubstateClusteringReport:
        samples = sorted(samples, key=lambda item: item.trade_date)
        feature_names = [
            "product_price_change_proxy",
            "demand_acceleration_proxy",
            "supply_tightness_proxy",
            "official_or_industry_catalyst_presence",
            "revenue_sensitivity_class",
            "gross_margin_sensitivity_class",
            "order_or_capacity_sensitivity_proxy",
            "earnings_revision_pressure_proxy",
            "rerating_gap_proxy",
            "relative_strength_persistence",
            "volume_expansion_confirmation",
            "breakout_or_hold_structure",
            "catalyst_freshness_state",
            "cross_day_catalyst_persistence",
            "theme_breadth_confirmation_proxy",
        ]
        classes = sorted(set(sample.label for sample in samples))
        label_to_int = {label: idx for idx, label in enumerate(classes)}
        x = np.array([[sample.feature_values[name] for name in feature_names] for sample in samples], dtype=float)
        y = np.array([label_to_int[sample.label] for sample in samples], dtype=int)
        split_index = max(1, min(len(samples) - 1, int(len(samples) * 0.7)))
        x_train, x_test = x[:split_index], x[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]
        train_samples = samples[:split_index]
        test_samples = samples[split_index:]

        baseline_preds = self._predict_nearest_centroid(x_train=x_train, y_train=y_train, x_test=x_test)
        gbdt_preds = self._predict_gbdt(x_train=x_train, y_train=y_train, x_test=x_test)

        cluster_groups: dict[str, list[TrainingSample]] = defaultdict(list)
        for sample in samples:
            cluster_groups[self._cluster_name(sample)].append(sample)

        cluster_rows: list[dict[str, Any]] = []
        for cluster_name, rows in sorted(cluster_groups.items(), key=lambda item: (self._cluster_priority(item[0]), item[0])):
            test_rows = [row for row in rows if row in test_samples]
            baseline_test_rows = self._rows_with_predictions(rows=test_rows, test_samples=test_samples, preds=baseline_preds, classes=classes)
            gbdt_test_rows = self._rows_with_predictions(rows=test_rows, test_samples=test_samples, preds=gbdt_preds, classes=classes)
            representatives = self._representatives(rows=rows)
            cluster_rows.append(
                {
                    "candidate_substate_name": cluster_name,
                    "candidate_substate_reading": self._cluster_reading(cluster_name),
                    "sample_count_total": len(rows),
                    "sample_count_train": sum(1 for row in rows if row in train_samples),
                    "sample_count_test": len(test_rows),
                    "label_distribution_total": self._distribution(row.label for row in rows),
                    "label_distribution_test": self._distribution(row.label for row in test_rows),
                    "mean_semantic_v2_features": self._mean_features(
                        rows=rows,
                        feature_names=[
                            "catalyst_freshness_state",
                            "cross_day_catalyst_persistence",
                            "theme_breadth_confirmation_proxy",
                        ],
                    ),
                    "mean_support_features": self._mean_features(
                        rows=rows,
                        feature_names=[
                            "product_price_change_proxy",
                            "demand_acceleration_proxy",
                            "relative_strength_persistence",
                            "volume_expansion_confirmation",
                            "breakout_or_hold_structure",
                        ],
                    ),
                    "representative_rows": representatives,
                    "baseline_v2_test_accuracy_in_cluster": self._cluster_accuracy(baseline_test_rows),
                    "baseline_v2_test_carry_fp_count_in_cluster": self._cluster_false_positives(baseline_test_rows),
                    "gbdt_v2_test_accuracy_in_cluster": self._cluster_accuracy(gbdt_test_rows),
                    "gbdt_v2_test_carry_fp_count_in_cluster": self._cluster_false_positives(gbdt_test_rows),
                    "support_level": "thin" if len(rows) < 5 else "strong",
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112h_candidate_substate_clustering_draft_v1",
            "candidate_cluster_count": len(cluster_rows),
            "high_level_consolidation_sample_count": len(samples),
            "test_fold_sample_count": len(test_samples),
            "high_level_consolidation_label_distribution": self._distribution(row.label for row in samples),
            "candidate_clusters_with_nontrivial_support": sum(1 for row in cluster_rows if int(row["sample_count_total"]) >= 5),
            "baseline_v2_test_accuracy": float(baseline_summary.get("baseline_v2_test_accuracy", 0.0)),
            "gbdt_v2_test_accuracy": float(gbdt_summary.get("gbdt_v2_test_accuracy", 0.0)),
            "ready_for_owner_review_next": True,
        }
        interpretation = [
            "The current high_level_consolidation label is likely too coarse to be treated as a single state.",
            "The cluster draft is review-only and does not define formal new labels.",
            "One cluster is sparse and should stay provisional, but the full set still suggests multiple candidate substates with different semantic profiles and misread behavior.",
        ]
        return V112HCandidateSubstateClusteringReport(summary=summary, cluster_rows=cluster_rows, interpretation=interpretation)

    def _cluster_name(self, sample: TrainingSample) -> str:
        breadth = float(sample.feature_values["theme_breadth_confirmation_proxy"])
        freshness = float(sample.feature_values["catalyst_freshness_state"])
        persistence = float(sample.feature_values["cross_day_catalyst_persistence"])
        breadth_high = breadth >= 0.5
        freshness_high = freshness >= 0.05
        persistence_high = persistence >= 0.1
        if breadth_high and freshness_high and persistence_high:
            return "breadth_rich_catalyst_active"
        if breadth_high and not (freshness_high or persistence_high):
            return "breadth_rich_catalyst_stale"
        if (not breadth_high) and (freshness_high or persistence_high):
            return "breadth_thin_catalyst_active"
        return "breadth_thin_catalyst_stale"

    def _cluster_priority(self, cluster_name: str) -> int:
        order = {
            "breadth_rich_catalyst_active": 0,
            "breadth_rich_catalyst_stale": 1,
            "breadth_thin_catalyst_active": 2,
            "breadth_thin_catalyst_stale": 3,
        }
        return order.get(cluster_name, 99)

    def _cluster_reading(self, cluster_name: str) -> str:
        readings = {
            "breadth_rich_catalyst_active": "Broad consolidation with both fresh catalyst and persistence support; the strongest candidate for a continuation-like substate.",
            "breadth_rich_catalyst_stale": "Broad consolidation where breadth remains present but catalyst freshness/persistence have faded; looks like a plateau or late stall candidate.",
            "breadth_thin_catalyst_active": "Narrow-breadth consolidation with active catalyst pressure; looks like a catalyst-led transition state rather than a broad breadth state.",
            "breadth_thin_catalyst_stale": "Narrow-breadth and low-catalyst consolidation; a large mixed bucket that likely hides several weaker sub-modes.",
        }
        return readings.get(cluster_name, "")

    def _distribution(self, labels) -> dict[str, int]:
        return dict(sorted(Counter(str(label) for label in labels).items()))

    def _mean_features(self, *, rows: list[TrainingSample], feature_names: list[str]) -> dict[str, float]:
        if not rows:
            return {name: 0.0 for name in feature_names}
        return {
            name: round(float(sum(float(row.feature_values[name]) for row in rows) / len(rows)), 6)
            for name in feature_names
        }

    def _representatives(self, *, rows: list[TrainingSample]) -> list[dict[str, Any]]:
        if not rows:
            return []
        feature_names = self.CLUSTER_FEATURE_NAMES
        matrix = np.array([[float(row.feature_values[name]) for name in feature_names] for row in rows], dtype=float)
        center = matrix.mean(axis=0)
        distances = np.linalg.norm(matrix - center, axis=1)
        ordered_indices = list(np.argsort(distances)[: min(3, len(rows))])
        return [
            {
                "trade_date": rows[idx].trade_date,
                "symbol": rows[idx].symbol,
                "true_label": rows[idx].label,
                "distance_to_cluster_center": round(float(distances[idx]), 6),
                "theme_breadth_confirmation_proxy": round(float(rows[idx].feature_values["theme_breadth_confirmation_proxy"]), 6),
                "catalyst_freshness_state": round(float(rows[idx].feature_values["catalyst_freshness_state"]), 6),
                "cross_day_catalyst_persistence": round(float(rows[idx].feature_values["cross_day_catalyst_persistence"]), 6),
            }
            for idx in ordered_indices
        ]

    def _predict_nearest_centroid(self, *, x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> np.ndarray:
        mean = x_train.mean(axis=0)
        std = x_train.std(axis=0)
        std[std == 0.0] = 1.0
        x_train_scaled = (x_train - mean) / std
        x_test_scaled = (x_test - mean) / std
        centroids = []
        centroid_classes = []
        for class_id in sorted(set(int(v) for v in y_train)):
            centroids.append(x_train_scaled[y_train == class_id].mean(axis=0))
            centroid_classes.append(class_id)
        centroid_matrix = np.vstack(centroids)
        preds = []
        for row in x_test_scaled:
            distances = np.linalg.norm(centroid_matrix - row, axis=1)
            preds.append(int(centroid_classes[int(np.argmin(distances))]))
        return np.array(preds, dtype=int)

    def _predict_gbdt(self, *, x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> np.ndarray:
        model = HistGradientBoostingClassifier(
            max_depth=4,
            learning_rate=0.05,
            max_iter=150,
            random_state=42,
        )
        model.fit(x_train, y_train)
        return np.asarray(model.predict(x_test), dtype=int)

    def _rows_with_predictions(
        self,
        *,
        rows: list[TrainingSample],
        test_samples: list[TrainingSample],
        preds: np.ndarray,
        classes: list[str],
    ) -> list[dict[str, Any]]:
        if not rows:
            return []
        test_index = {id(sample): idx for idx, sample in enumerate(test_samples)}
        output = []
        for row in rows:
            idx = test_index.get(id(row))
            if idx is None:
                continue
            output.append(
                {
                    "trade_date": row.trade_date,
                    "symbol": row.symbol,
                    "predicted_label": classes[int(preds[idx])],
                    "true_label": row.label,
                    "correct": classes[int(preds[idx])] == row.label,
                }
            )
        return output

    def _cluster_accuracy(self, rows: list[dict[str, Any]]) -> float:
        if not rows:
            return 0.0
        return round(float(sum(1 for row in rows if bool(row.get("correct"))) / len(rows)), 4)

    def _cluster_false_positives(self, rows: list[dict[str, Any]]) -> int:
        total = 0
        for row in rows:
            if str(row.get("predicted_label")) == "carry_constructive" and str(row.get("true_label")) != "carry_constructive":
                total += 1
        return total


def write_v112h_candidate_substate_clustering_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112HCandidateSubstateClusteringReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
