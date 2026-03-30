from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(slots=True)
class TrainingSample:
    sample_id: str
    label: str
    features: dict[str, float]


@dataclass(slots=True)
class V12BoundedTrainingPilotReport:
    summary: dict[str, Any]
    feature_names: list[str]
    sample_rows: list[dict[str, Any]]
    fold_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_names": self.feature_names,
            "sample_rows": self.sample_rows,
            "fold_rows": self.fold_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def _layer_to_value(layer: str | None) -> float:
    mapping = {
        "junk": 0.0,
        "core": 1.0,
        "late_mover": 2.0,
        "leader": 3.0,
    }
    return mapping.get(str(layer), -1.0)


def _count_true(iterable: list[bool]) -> int:
    return sum(1 for item in iterable if item)


class V12BoundedTrainingPilotAnalyzer:
    """Run a tiny report-only training pilot on frozen structured lane artifacts."""

    FEATURE_NAMES = [
        "assignment_layer_value",
        "specialist_permission_allowed",
        "specialist_trigger_count",
        "specialist_filter_count",
        "anchor_count",
        "anchor_alignment_present",
        "anchor_junk_block_present",
        "specialist_position_present",
        "specialist_holding_health_score",
        "anchor_exit_signal_count",
        "basis_advantage_bps",
        "challenger_carry_days",
        "same_exit_date",
        "pnl_delta_vs_closest",
    ]

    def _opening_sample(self, *, sample_id: str, payload: dict[str, Any]) -> TrainingSample:
        opening_edge = dict(payload.get("opening_edge") or {})
        anchor_blockers = list(payload.get("anchor_blockers", []))
        features = {
            "assignment_layer_value": _layer_to_value(opening_edge.get("specialist_assignment_layer")),
            "specialist_permission_allowed": float(bool(opening_edge.get("specialist_permission_allowed"))),
            "specialist_trigger_count": float(len(list(opening_edge.get("specialist_triggered_entries", [])))),
            "specialist_filter_count": float(len(list(opening_edge.get("specialist_passed_filters", [])))),
            "anchor_count": float(len(anchor_blockers)),
            "anchor_alignment_present": float(
                bool(anchor_blockers)
                and all(
                    bool(row.get("permission_allowed")) and not list(row.get("emitted_actions", []))
                    for row in anchor_blockers
                )
            ),
            "anchor_junk_block_present": float(
                bool(anchor_blockers)
                and all(str(row.get("assignment_layer")) == "junk" for row in anchor_blockers)
            ),
            "specialist_position_present": 0.0,
            "specialist_holding_health_score": 0.0,
            "anchor_exit_signal_count": 0.0,
            "basis_advantage_bps": 0.0,
            "challenger_carry_days": 0.0,
            "same_exit_date": 0.0,
            "pnl_delta_vs_closest": 0.0,
        }
        return TrainingSample(sample_id=sample_id, label="opening_led", features=features)

    def _persistence_sample(self, *, sample_id: str, payload: dict[str, Any]) -> TrainingSample:
        edge = dict(payload.get("persistence_edge") or {})
        anchor_divergence = list(payload.get("anchor_divergence", []))
        features = {
            "assignment_layer_value": _layer_to_value(edge.get("specialist_assignment_layer")),
            "specialist_permission_allowed": 0.0,
            "specialist_trigger_count": 0.0,
            "specialist_filter_count": 0.0,
            "anchor_count": float(len(anchor_divergence)),
            "anchor_alignment_present": 0.0,
            "anchor_junk_block_present": float(
                bool(anchor_divergence)
                and all(str(row.get("assignment_layer")) == "junk" for row in anchor_divergence)
            ),
            "specialist_position_present": float(float(edge.get("specialist_position_qty", 0.0)) > 0.0),
            "specialist_holding_health_score": float(edge.get("specialist_holding_health_score", 0.0) or 0.0),
            "anchor_exit_signal_count": float(
                _count_true([bool(row.get("exit_should_exit")) for row in anchor_divergence])
            ),
            "basis_advantage_bps": 0.0,
            "challenger_carry_days": 0.0,
            "same_exit_date": 0.0,
            "pnl_delta_vs_closest": 0.0,
        }
        return TrainingSample(sample_id=sample_id, label="persistence_led", features=features)

    def _carry_samples(self, *, sample_id_prefix: str, payload: dict[str, Any]) -> list[TrainingSample]:
        rows = list(payload.get("schema_rows", []))
        samples: list[TrainingSample] = []
        for idx, row in enumerate(rows, start=1):
            features = {
                "assignment_layer_value": 0.0,
                "specialist_permission_allowed": 0.0,
                "specialist_trigger_count": 0.0,
                "specialist_filter_count": 0.0,
                "anchor_count": 0.0,
                "anchor_alignment_present": 0.0,
                "anchor_junk_block_present": 0.0,
                "specialist_position_present": 0.0,
                "specialist_holding_health_score": 0.0,
                "anchor_exit_signal_count": 0.0,
                "basis_advantage_bps": float(row.get("basis_advantage_bps", 0.0)),
                "challenger_carry_days": float(row.get("challenger_carry_days", 0.0)),
                "same_exit_date": float(bool(row.get("same_exit_date"))),
                "pnl_delta_vs_closest": float(row.get("pnl_delta_vs_closest", 0.0)),
            }
            samples.append(
                TrainingSample(
                    sample_id=f"{sample_id_prefix}_{idx}",
                    label="carry_row_present",
                    features=features,
                )
            )
        return samples

    def _stack(self, samples: list[TrainingSample]) -> tuple[np.ndarray, np.ndarray, list[str]]:
        feature_matrix = np.array(
            [[sample.features[name] for name in self.FEATURE_NAMES] for sample in samples],
            dtype=float,
        )
        labels = [sample.label for sample in samples]
        classes = sorted(set(labels))
        label_matrix = np.array([classes.index(label) for label in labels], dtype=int)
        return feature_matrix, label_matrix, classes

    def _loocv_nearest_centroid(
        self,
        feature_matrix: np.ndarray,
        label_matrix: np.ndarray,
        classes: list[str],
    ) -> list[dict[str, Any]]:
        fold_rows: list[dict[str, Any]] = []
        for idx in range(feature_matrix.shape[0]):
            train_mask = np.ones(feature_matrix.shape[0], dtype=bool)
            train_mask[idx] = False
            x_train = feature_matrix[train_mask]
            y_train = label_matrix[train_mask]
            x_test = feature_matrix[idx : idx + 1]
            y_true = int(label_matrix[idx])

            mean = x_train.mean(axis=0)
            std = x_train.std(axis=0)
            std[std == 0.0] = 1.0
            x_train_scaled = (x_train - mean) / std
            x_test_scaled = (x_test - mean) / std

            centroids = []
            centroid_classes = []
            for class_idx in sorted(set(int(v) for v in y_train)):
                centroids.append(x_train_scaled[y_train == class_idx].mean(axis=0))
                centroid_classes.append(class_idx)
            centroid_matrix = np.vstack(centroids)
            distances = np.linalg.norm(centroid_matrix - x_test_scaled[0], axis=1)
            pred_class = int(centroid_classes[int(np.argmin(distances))])
            fold_rows.append(
                {
                    "fold_index": idx,
                    "predicted_label": classes[pred_class],
                    "true_label": classes[y_true],
                    "correct": pred_class == y_true,
                }
            )
        return fold_rows

    def analyze(
        self,
        *,
        opening_payloads: list[tuple[str, dict[str, Any]]],
        persistence_payloads: list[tuple[str, dict[str, Any]]],
        carry_payload: dict[str, Any],
    ) -> V12BoundedTrainingPilotReport:
        samples: list[TrainingSample] = []
        for sample_id, payload in opening_payloads:
            samples.append(self._opening_sample(sample_id=sample_id, payload=payload))
        for sample_id, payload in persistence_payloads:
            samples.append(self._persistence_sample(sample_id=sample_id, payload=payload))
        samples.extend(self._carry_samples(sample_id_prefix="carry", payload=carry_payload))

        feature_matrix, label_matrix, classes = self._stack(samples)
        fold_rows = self._loocv_nearest_centroid(feature_matrix, label_matrix, classes)
        accuracy = sum(1 for row in fold_rows if bool(row["correct"])) / len(fold_rows)

        class_accuracy: dict[str, float] = {}
        for label in classes:
            subset = [row for row in fold_rows if row["true_label"] == label]
            class_accuracy[label] = sum(1 for row in subset if bool(row["correct"])) / len(subset)

        summary = {
            "pilot_posture": "open_v12_bounded_training_pilot_as_report_only",
            "model_type": "leave_one_out_nearest_centroid",
            "sample_count": len(samples),
            "class_count": len(classes),
            "class_labels": classes,
            "overall_accuracy": round(float(accuracy), 4),
            "class_accuracy": {k: round(float(v), 4) for k, v in class_accuracy.items()},
            "allow_strategy_training_now": False,
            "allow_news_branch_training_now": False,
        }
        sample_rows = [
            {
                "sample_id": sample.sample_id,
                "label": sample.label,
                **sample.features,
            }
            for sample in samples
        ]
        interpretation = [
            "This is a bounded training pilot on frozen structured lane artifacts, not a production model and not a strategy-integrated ML branch.",
            "The pilot only tests whether current structured observables can separate opening-led, persistence-led, and carry-row-present lanes at all.",
            "Even if the micro-pilot separates classes well, that only justifies later feature work; it does not justify live strategy training or raw-news model integration.",
        ]
        return V12BoundedTrainingPilotReport(
            summary=summary,
            feature_names=self.FEATURE_NAMES,
            sample_rows=sample_rows,
            fold_rows=fold_rows,
            interpretation=interpretation,
        )


def write_v12_bounded_training_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12BoundedTrainingPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
