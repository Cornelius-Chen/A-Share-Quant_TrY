from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


def _to_float(value: Any, default: float = 0.0) -> float:
    text = str(value).strip()
    if text == "":
        return default
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def write_csv_rows(*, path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def _accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) == 0:
        return 0.0
    return float(np.mean(y_true == y_pred))


def _macro_precision_recall(y_true: np.ndarray, y_pred: np.ndarray, classes: list[int]) -> tuple[float, float]:
    precision_values: list[float] = []
    recall_values: list[float] = []
    for cls in classes:
        tp = int(np.sum((y_true == cls) & (y_pred == cls)))
        fp = int(np.sum((y_true != cls) & (y_pred == cls)))
        fn = int(np.sum((y_true == cls) & (y_pred != cls)))
        precision_values.append(tp / (tp + fp) if (tp + fp) > 0 else 0.0)
        recall_values.append(tp / (tp + fn) if (tp + fn) > 0 else 0.0)
    return float(_mean(precision_values)), float(_mean(recall_values))


def _confusion_rows(y_true: np.ndarray, y_pred: np.ndarray, class_names: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for true_idx, true_name in enumerate(class_names):
        for pred_idx, pred_name in enumerate(class_names):
            rows.append(
                {
                    "true_label": true_name,
                    "predicted_label": pred_name,
                    "count": int(np.sum((y_true == true_idx) & (y_pred == pred_idx))),
                }
            )
    return rows


@dataclass(slots=True)
class V115ICpoHighDimensionalIntradayActionTrainingPilotReport:
    summary: dict[str, Any]
    class_count_rows: list[dict[str, Any]]
    feature_rank_rows: list[dict[str, Any]]
    model_rows: list[dict[str, Any]]
    confusion_rows: list[dict[str, Any]]
    sample_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "class_count_rows": self.class_count_rows,
            "feature_rank_rows": self.feature_rank_rows,
            "model_rows": self.model_rows,
            "confusion_rows": self.confusion_rows,
            "sample_rows": self.sample_rows,
            "interpretation": self.interpretation,
        }


class V115ICpoHighDimensionalIntradayActionTrainingPilotAnalyzer:
    CONTINUOUS_RZ_FEATURES = [
        "f30_breakout_efficiency_rz",
        "f60_breakout_efficiency_rz",
        "f30_close_vs_vwap_rz",
        "f60_close_vs_vwap_rz",
        "f30_close_location_rz",
        "f60_close_location_rz",
        "f30_pullback_from_high_rz",
        "f60_pullback_from_high_rz",
        "f30_last_bar_return_rz",
        "f60_last_bar_return_rz",
        "f30_last_bar_volume_share_rz",
        "f60_last_bar_volume_share_rz",
        "f30_high_time_ratio_rz",
        "f60_high_time_ratio_rz",
        "f30_afternoon_volume_share_rz",
        "f60_afternoon_volume_share_rz",
        "f30_upper_shadow_ratio_rz",
        "f60_upper_shadow_ratio_rz",
        "f30_lower_shadow_ratio_rz",
        "f60_lower_shadow_ratio_rz",
        "f30_body_ratio_rz",
        "f60_body_ratio_rz",
        "f30_last_bar_upper_shadow_ratio_rz",
        "f60_last_bar_upper_shadow_ratio_rz",
        "f30_last_bar_lower_shadow_ratio_rz",
        "f60_last_bar_lower_shadow_ratio_rz",
        "d5_30_close_vs_vwap_rz",
        "d15_60_close_vs_vwap_rz",
        "d5_30_last_bar_return_rz",
        "d15_60_last_bar_return_rz",
        "d5_30_last_bar_volume_share_rz",
        "d15_60_last_bar_volume_share_rz",
        "d5_30_upper_shadow_ratio_rz",
        "d15_60_upper_shadow_ratio_rz",
        "d5_30_lower_shadow_ratio_rz",
        "d15_60_lower_shadow_ratio_rz",
        "d5_30_last_bar_upper_shadow_ratio_rz",
        "d15_60_last_bar_upper_shadow_ratio_rz",
        "d5_30_last_bar_lower_shadow_ratio_rz",
        "d15_60_last_bar_lower_shadow_ratio_rz",
    ]
    BINARY_FEATURES = [
        "f30_failed_push_proxy",
        "f60_failed_push_proxy",
        "d15_60_failed_push_proxy",
    ]
    FEATURE_COLUMNS = CONTINUOUS_RZ_FEATURES + BINARY_FEATURES
    LABEL_NAMES = ["hold_or_skip", "increase_expression", "decrease_expression"]

    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @classmethod
    def _coarse_label(cls, row: dict[str, Any]) -> str:
        action_context = str(row.get("action_context", ""))
        favored = str(row.get("action_favored_3d", "")) == "True"
        if action_context in {"entry_vs_skip", "add_vs_hold"} and favored:
            return "increase_expression"
        if action_context in {"reduce_vs_hold", "close_vs_hold"} and favored:
            return "decrease_expression"
        return "hold_or_skip"

    @staticmethod
    def _date_split(rows: list[dict[str, Any]], split_ratio: float = 0.7) -> tuple[set[str], set[str]]:
        unique_dates = sorted({str(row["signal_trade_date"]) for row in rows})
        split_index = max(1, min(len(unique_dates) - 1, int(len(unique_dates) * split_ratio)))
        return set(unique_dates[:split_index]), set(unique_dates[split_index:])

    @staticmethod
    def _balanced_class_weights(train_labels: list[str]) -> dict[str, float]:
        counts: dict[str, int] = {}
        for label in train_labels:
            counts[label] = counts.get(label, 0) + 1
        class_count = max(len(counts), 1)
        total = max(len(train_labels), 1)
        return {
            label: total / (class_count * count)
            for label, count in counts.items()
        }

    @classmethod
    def _feature_ranking(cls, train_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ranked: list[dict[str, Any]] = []
        for feature_name in cls.FEATURE_COLUMNS:
            inc_values = [_to_float(row.get(feature_name)) for row in train_rows if row["coarse_label"] == "increase_expression"]
            hold_values = [_to_float(row.get(feature_name)) for row in train_rows if row["coarse_label"] == "hold_or_skip"]
            dec_values = [_to_float(row.get(feature_name)) for row in train_rows if row["coarse_label"] == "decrease_expression"]
            inc_mean = _mean(inc_values)
            hold_mean = _mean(hold_values)
            dec_mean = _mean(dec_values)
            score = abs(inc_mean - hold_mean) + abs(inc_mean - dec_mean) + 0.5 * abs(hold_mean - dec_mean)
            ranked.append(
                {
                    "feature_name": feature_name,
                    "increase_mean": round(inc_mean, 6),
                    "hold_mean": round(hold_mean, 6),
                    "decrease_mean": round(dec_mean, 6),
                    "screen_score": round(score, 6),
                }
            )
        ranked.sort(key=lambda row: float(row["screen_score"]), reverse=True)
        return ranked

    @staticmethod
    def _matrix(rows: list[dict[str, Any]], feature_names: list[str]) -> np.ndarray:
        return np.array(
            [[_to_float(row.get(feature_name)) for feature_name in feature_names] for row in rows],
            dtype=float,
        )

    def _nearest_centroid_predictions(
        self,
        *,
        x_train: np.ndarray,
        y_train: np.ndarray,
        class_weights_vec: np.ndarray,
        x_test: np.ndarray,
    ) -> np.ndarray:
        classes = sorted(set(int(value) for value in y_train))
        centroids = []
        for cls in classes:
            mask = y_train == cls
            weights = class_weights_vec[mask]
            subset = x_train[mask]
            centroid = np.average(subset, axis=0, weights=weights)
            centroids.append(centroid)
        centroid_matrix = np.vstack(centroids)
        preds: list[int] = []
        for row in x_test:
            distances = np.linalg.norm(centroid_matrix - row, axis=1)
            preds.append(classes[int(np.argmin(distances))])
        return np.array(preds, dtype=int)

    def _weighted_ridge_predictions(
        self,
        *,
        x_train: np.ndarray,
        y_train: np.ndarray,
        class_weights_vec: np.ndarray,
        x_test: np.ndarray,
        class_count: int,
        alpha: float = 1.0,
    ) -> np.ndarray:
        y_onehot = np.zeros((len(y_train), class_count), dtype=float)
        for idx, cls in enumerate(y_train):
            y_onehot[idx, int(cls)] = 1.0
        x_aug = np.hstack([np.ones((len(x_train), 1), dtype=float), x_train])
        x_test_aug = np.hstack([np.ones((len(x_test), 1), dtype=float), x_test])
        w_sqrt = np.sqrt(class_weights_vec)
        xw = x_aug * w_sqrt[:, None]
        yw = y_onehot * w_sqrt[:, None]
        gram = xw.T @ xw
        gram += alpha * np.eye(gram.shape[0], dtype=float)
        coef = np.linalg.pinv(gram) @ (xw.T @ yw)
        scores = x_test_aug @ coef
        return np.argmax(scores, axis=1).astype(int)

    @classmethod
    def _model_row(
        cls,
        *,
        model_name: str,
        y_test: np.ndarray,
        y_pred: np.ndarray,
        test_rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        accuracy = _accuracy_score(y_test, y_pred)
        macro_precision, macro_recall = _macro_precision_recall(y_test, y_pred, list(range(len(cls.LABEL_NAMES))))

        predicted_increase_rows = [
            row for idx, row in enumerate(test_rows) if int(y_pred[idx]) == cls.LABEL_NAMES.index("increase_expression")
        ]
        predicted_decrease_rows = [
            row for idx, row in enumerate(test_rows) if int(y_pred[idx]) == cls.LABEL_NAMES.index("decrease_expression")
        ]

        return {
            "model_name": model_name,
            "test_accuracy": round(accuracy, 6),
            "macro_precision": round(macro_precision, 6),
            "macro_recall": round(macro_recall, 6),
            "predicted_increase_count": len(predicted_increase_rows),
            "predicted_decrease_count": len(predicted_decrease_rows),
            "predicted_increase_avg_expectancy_proxy_3d": round(
                _mean([_to_float(row.get("expectancy_proxy_3d")) for row in predicted_increase_rows]), 6
            ),
            "predicted_increase_avg_max_adverse_return_3d": round(
                _mean([_to_float(row.get("max_adverse_return_3d")) for row in predicted_increase_rows]), 6
            ),
            "predicted_decrease_avg_expectancy_proxy_3d": round(
                _mean([_to_float(row.get("expectancy_proxy_3d")) for row in predicted_decrease_rows]), 6
            ),
            "predicted_decrease_avg_max_adverse_return_3d": round(
                _mean([_to_float(row.get("max_adverse_return_3d")) for row in predicted_decrease_rows]), 6
            ),
        }

    def analyze(self, *, base_rows: list[dict[str, Any]]) -> tuple[V115ICpoHighDimensionalIntradayActionTrainingPilotReport, list[dict[str, Any]]]:
        rows = [dict(row) for row in base_rows]
        for row in rows:
            row["coarse_label"] = self._coarse_label(row)

        train_dates, test_dates = self._date_split(rows)
        for row in rows:
            row["split_group"] = "train" if str(row["signal_trade_date"]) in train_dates else "test"

        train_rows = [row for row in rows if row["split_group"] == "train"]
        test_rows = [row for row in rows if row["split_group"] == "test"]

        class_weights = self._balanced_class_weights([str(row["coarse_label"]) for row in train_rows])
        for row in rows:
            row["row_weight"] = round(class_weights[str(row["coarse_label"])], 6)

        feature_rank_rows = self._feature_ranking(train_rows)
        selected_feature_names = [str(row["feature_name"]) for row in feature_rank_rows[:12]]

        x_train = self._matrix(train_rows, selected_feature_names)
        x_test = self._matrix(test_rows, selected_feature_names)
        label_to_int = {name: idx for idx, name in enumerate(self.LABEL_NAMES)}
        y_train = np.array([label_to_int[str(row["coarse_label"])] for row in train_rows], dtype=int)
        y_test = np.array([label_to_int[str(row["coarse_label"])] for row in test_rows], dtype=int)
        weight_vec = np.array([class_weights[str(row["coarse_label"])] for row in train_rows], dtype=float)

        nearest_preds = self._nearest_centroid_predictions(
            x_train=x_train,
            y_train=y_train,
            class_weights_vec=weight_vec,
            x_test=x_test,
        )
        ridge_preds = self._weighted_ridge_predictions(
            x_train=x_train,
            y_train=y_train,
            class_weights_vec=weight_vec,
            x_test=x_test,
            class_count=len(self.LABEL_NAMES),
            alpha=1.0,
        )

        model_rows = [
            self._model_row(model_name="weighted_nearest_centroid_guardrail", y_test=y_test, y_pred=nearest_preds, test_rows=test_rows),
            self._model_row(model_name="weighted_ridge_multiclass_candidate", y_test=y_test, y_pred=ridge_preds, test_rows=test_rows),
        ]

        best_model = max(model_rows, key=lambda row: float(row["macro_recall"]))
        class_count_rows = []
        for label_name in self.LABEL_NAMES:
            class_count_rows.append(
                {
                    "coarse_label": label_name,
                    "train_count": sum(1 for row in train_rows if str(row["coarse_label"]) == label_name),
                    "test_count": sum(1 for row in test_rows if str(row["coarse_label"]) == label_name),
                    "effective_row_weight": round(class_weights.get(label_name, 0.0), 6),
                }
            )

        confusion_rows = _confusion_rows(y_true=y_test, y_pred=ridge_preds, class_names=self.LABEL_NAMES)
        summary = {
            "acceptance_posture": "freeze_v115i_cpo_high_dimensional_intraday_action_training_pilot_v1",
            "base_row_count": len(rows),
            "train_row_count": len(train_rows),
            "test_row_count": len(test_rows),
            "coarse_label_count": len(self.LABEL_NAMES),
            "selected_feature_count": len(selected_feature_names),
            "selected_feature_names": selected_feature_names,
            "smallest_train_class_count": min(int(row["train_count"]) for row in class_count_rows),
            "balanced_training_view_built": True,
            "candidate_only_pilot": True,
            "best_model_by_macro_recall": best_model["model_name"],
            "best_model_macro_recall": best_model["macro_recall"],
            "recommended_next_posture": "use_v115i_as_candidate_training_pilot_only_then_run_unsupervised_discovery_on_v115h_base_table",
        }
        interpretation = [
            "V1.15I does not treat the high-dimensional intraday table as a law engine. It first converts it into a weighted, balanced training view with coarse action-expression labels.",
            "The purpose is to test whether the V115H feature base can support guarded action learning at all before any unsupervised states are promoted back into execution logic.",
            "This remains candidate-only because the increase-expression class is still very small and all labels still inherit repaired replay path dependence.",
        ]
        report = V115ICpoHighDimensionalIntradayActionTrainingPilotReport(
            summary=summary,
            class_count_rows=class_count_rows,
            feature_rank_rows=feature_rank_rows,
            model_rows=model_rows,
            confusion_rows=confusion_rows,
            sample_rows=rows[:8],
            interpretation=interpretation,
        )
        return report, rows


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V115ICpoHighDimensionalIntradayActionTrainingPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    with (repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv").open("r", encoding="utf-8") as handle:
        base_rows = list(csv.DictReader(handle))
    analyzer = V115ICpoHighDimensionalIntradayActionTrainingPilotAnalyzer(repo_root=repo_root)
    result, training_view_rows = analyzer.analyze(base_rows=base_rows)
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv",
        rows=training_view_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115i_cpo_high_dimensional_intraday_action_training_pilot_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
