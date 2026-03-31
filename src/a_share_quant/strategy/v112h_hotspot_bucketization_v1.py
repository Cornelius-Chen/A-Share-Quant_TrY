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
class V112HHotspotBucketizationReport:
    summary: dict[str, Any]
    bucket_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "bucket_rows": self.bucket_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112HHotspotBucketizationAnalyzer:
    FEATURE_NAMES = list(V112GBaselineReadoutV2Analyzer.FEATURE_NAMES)

    def analyze(
        self,
        *,
        pilot_dataset_payload: dict[str, Any],
        baseline_v2_payload: dict[str, Any],
        gbdt_v2_payload: dict[str, Any],
    ) -> V112HHotspotBucketizationReport:
        baseline_summary = dict(baseline_v2_payload.get("summary", {}))
        gbdt_summary = dict(gbdt_v2_payload.get("summary", {}))
        if not bool(baseline_summary.get("ready_for_gbdt_v2_next")):
            raise ValueError("V1.12H hotspot bucketization requires the frozen V1.12G baseline v2 report.")
        if not bool(gbdt_summary.get("ready_for_phase_check_next")):
            raise ValueError("V1.12H hotspot bucketization requires the frozen V1.12G GBDT v2 report.")

        analyzer = V112GBaselineReadoutV2Analyzer()
        samples = analyzer.build_augmented_samples(pilot_dataset_payload=pilot_dataset_payload)
        records = self._build_prediction_records(samples=samples)
        target_records = [
            record
            for record in records
            if record["stage"] in {"high_level_consolidation", "major_markup"}
            and (not bool(record["baseline_correct"]) or not bool(record["gbdt_correct"]))
        ]
        if not target_records:
            raise ValueError("V1.12H hotspot bucketization requires misread rows from the two hotspot stages.")

        bucket_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in target_records:
            bucket_groups[self._bucket_name(record)].append(record)

        bucket_rows = []
        for bucket_name, rows in sorted(bucket_groups.items(), key=lambda item: (self._bucket_priority(item[0]), item[0])):
            bucket_rows.append(self._build_bucket_row(bucket_name=bucket_name, rows=rows))

        summary = {
            "acceptance_posture": "freeze_v112h_hotspot_bucketization_v1",
            "bucket_count": len(bucket_rows),
            "target_stage_count": 2,
            "target_stage_row_count": len(target_records),
            "baseline_misread_row_count": sum(1 for row in target_records if not bool(row["baseline_correct"])),
            "gbdt_misread_row_count": sum(1 for row in target_records if not bool(row["gbdt_correct"])),
            "both_models_misread_row_count": sum(
                1 for row in target_records if (not bool(row["baseline_correct"]) and not bool(row["gbdt_correct"]))
            ),
            "ready_for_owner_review_next": True,
        }
        interpretation = [
            "The misread rows are not random noise; they collapse into a small number of reviewable stage-plus-semantic buckets.",
            "The output is intentionally a bucket draft, not a formal label split.",
            "The next owner review can decide whether the largest bucket(s) justify bounded label refinement.",
        ]
        return V112HHotspotBucketizationReport(summary=summary, bucket_rows=bucket_rows, interpretation=interpretation)

    def _build_prediction_records(self, *, samples: list[TrainingSample]) -> list[dict[str, Any]]:
        ordered_samples = sorted(samples, key=lambda item: item.trade_date)
        feature_matrix = np.array([[sample.feature_values[name] for name in self.FEATURE_NAMES] for sample in ordered_samples], dtype=float)
        labels = [sample.label for sample in ordered_samples]
        classes = sorted(set(labels))
        label_ids = np.array([classes.index(label) for label in labels], dtype=int)
        split_index = max(1, min(len(ordered_samples) - 1, int(len(ordered_samples) * 0.7)))
        x_train = feature_matrix[:split_index]
        y_train = label_ids[:split_index]
        x_test = feature_matrix[split_index:]
        y_test = label_ids[split_index:]
        test_samples = ordered_samples[split_index:]

        baseline_preds = self._predict_nearest_centroid(x_train=x_train, y_train=y_train, x_test=x_test)
        gbdt_preds = self._predict_gbdt(x_train=x_train, y_train=y_train, x_test=x_test)

        records: list[dict[str, Any]] = []
        for idx, sample in enumerate(test_samples):
            baseline_pred = classes[int(baseline_preds[idx])]
            gbdt_pred = classes[int(gbdt_preds[idx])]
            true_label = classes[int(y_test[idx])]
            record = {
                "trade_date": sample.trade_date,
                "symbol": sample.symbol,
                "stage": sample.stage,
                "true_label": true_label,
                "baseline_predicted_label": baseline_pred,
                "baseline_correct": baseline_pred == true_label,
                "gbdt_predicted_label": gbdt_pred,
                "gbdt_correct": gbdt_pred == true_label,
                "feature_values": sample.feature_values,
            }
            records.append(record)
        return records

    def _bucket_name(self, record: dict[str, Any]) -> str:
        return f"{record['stage']}__{self._semantic_cluster(record['feature_values'])}"

    def _semantic_cluster(self, feature_values: dict[str, float]) -> str:
        breadth = float(feature_values["theme_breadth_confirmation_proxy"])
        freshness = float(feature_values["catalyst_freshness_state"])
        persistence = float(feature_values["cross_day_catalyst_persistence"])
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

    def _bucket_priority(self, bucket_name: str) -> int:
        order = {
            "high_level_consolidation__breadth_rich_catalyst_active": 0,
            "high_level_consolidation__breadth_rich_catalyst_stale": 1,
            "high_level_consolidation__breadth_thin_catalyst_active": 2,
            "high_level_consolidation__breadth_thin_catalyst_stale": 3,
            "major_markup__breadth_rich_catalyst_active": 4,
            "major_markup__breadth_rich_catalyst_stale": 5,
            "major_markup__breadth_thin_catalyst_active": 6,
            "major_markup__breadth_thin_catalyst_stale": 7,
        }
        return order.get(bucket_name, 99)

    def _bucket_reading(self, bucket_name: str) -> str:
        semantic_name = bucket_name.split("__", 1)[1] if "__" in bucket_name else bucket_name
        readings = {
            "breadth_rich_catalyst_active": "Broad and fresh catalyst pressure with cross-day persistence; the cleanest continuation-like bucket.",
            "breadth_rich_catalyst_stale": "Broad but stale consolidation; looks like breadth remains while catalyst freshness fades.",
            "breadth_thin_catalyst_active": "Thin breadth but active catalyst pressure; looks more like a catalyst-led transition pocket.",
            "breadth_thin_catalyst_stale": "Thin breadth and stale catalyst; likely the weakest mixed bucket and the most likely to hide multiple submodes.",
        }
        return readings.get(semantic_name, "")

    def _build_bucket_row(self, *, bucket_name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
        rows = sorted(rows, key=lambda item: (item["trade_date"], item["symbol"]))
        feature_names = ["catalyst_freshness_state", "cross_day_catalyst_persistence", "theme_breadth_confirmation_proxy"]
        semantics = {name: round(float(sum(float(row["feature_values"][name]) for row in rows) / len(rows)), 6) for name in feature_names}
        support_features = [
            "product_price_change_proxy",
            "demand_acceleration_proxy",
            "relative_strength_persistence",
            "volume_expansion_confirmation",
            "breakout_or_hold_structure",
        ]
        support_means = {
            name: round(float(sum(float(row["feature_values"][name]) for row in rows) / len(rows)), 6)
            for name in support_features
        }
        representative_rows = self._representatives(rows=rows, feature_names=feature_names)
        return {
            "bucket_name": bucket_name,
            "bucket_stage": rows[0]["stage"] if rows else "",
            "bucket_reading": self._bucket_reading(bucket_name),
            "sample_count": len(rows),
            "symbol_distribution": self._distribution(row["symbol"] for row in rows),
            "true_label_distribution": self._distribution(row["true_label"] for row in rows),
            "baseline_predicted_label_distribution": self._distribution(row["baseline_predicted_label"] for row in rows),
            "gbdt_predicted_label_distribution": self._distribution(row["gbdt_predicted_label"] for row in rows),
            "error_pattern_distribution": self._distribution(self._error_pattern(row) for row in rows),
            "mean_semantic_v2_features": semantics,
            "mean_support_features": support_means,
            "representative_rows": representative_rows,
            "baseline_only_misread_count": sum(1 for row in rows if (not bool(row["baseline_correct"]) and bool(row["gbdt_correct"]))),
            "gbdt_only_misread_count": sum(1 for row in rows if (bool(row["baseline_correct"]) and not bool(row["gbdt_correct"]))),
            "both_models_misread_count": sum(1 for row in rows if (not bool(row["baseline_correct"]) and not bool(row["gbdt_correct"]))),
        }

    def _representatives(self, *, rows: list[dict[str, Any]], feature_names: list[str]) -> list[dict[str, Any]]:
        if not rows:
            return []
        matrix = np.array([[float(row["feature_values"][name]) for name in feature_names] for row in rows], dtype=float)
        center = matrix.mean(axis=0)
        distances = np.linalg.norm(matrix - center, axis=1)
        ordered_indices = list(np.argsort(distances)[: min(3, len(rows))])
        return [
            {
                "trade_date": rows[idx]["trade_date"],
                "symbol": rows[idx]["symbol"],
                "stage": rows[idx]["stage"],
                "true_label": rows[idx]["true_label"],
                "baseline_predicted_label": rows[idx]["baseline_predicted_label"],
                "gbdt_predicted_label": rows[idx]["gbdt_predicted_label"],
                "error_pattern": self._error_pattern(rows[idx]),
                "distance_to_bucket_center": round(float(distances[idx]), 6),
                "theme_breadth_confirmation_proxy": round(float(rows[idx]["feature_values"]["theme_breadth_confirmation_proxy"]), 6),
                "catalyst_freshness_state": round(float(rows[idx]["feature_values"]["catalyst_freshness_state"]), 6),
                "cross_day_catalyst_persistence": round(float(rows[idx]["feature_values"]["cross_day_catalyst_persistence"]), 6),
            }
            for idx in ordered_indices
        ]

    def _error_pattern(self, row: dict[str, Any]) -> str:
        baseline_correct = bool(row["baseline_correct"])
        gbdt_correct = bool(row["gbdt_correct"])
        if baseline_correct and gbdt_correct:
            return "both_correct"
        if (not baseline_correct) and (not gbdt_correct):
            return "both_misread"
        if not baseline_correct:
            return "baseline_only"
        return "gbdt_only"

    def _distribution(self, labels) -> dict[str, int]:
        return dict(sorted(Counter(str(label) for label in labels).items()))

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


def write_v112h_hotspot_bucketization_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112HHotspotBucketizationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
