from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v128y_commercial_aerospace_state_machine_supervised_table_v1 import (
    V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer,
)


NUMERIC_FEATURES = [
    "trend_return_20",
    "up_day_rate",
    "liquidity_amount_mean",
    "turnover_rate_f_mean",
    "volume_ratio_mean",
    "elg_buy_sell_ratio_mean",
    "limit_heat_rate",
    "local_quality_support",
    "local_heat_support",
    "board_total_support",
    "board_non_theme_support",
    "board_heat_score",
    "board_event_drought",
]

CATEGORICAL_FEATURES = ["regime_proxy_semantic", "event_state", "phase_window_semantic"]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: list[float], mean: float) -> float:
    if not values:
        return 1.0
    var = sum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(var) or 1.0


def _balanced_accuracy(y_true: list[str], y_pred: list[str]) -> float:
    labels = sorted(set(y_true))
    recalls: list[float] = []
    for label in labels:
        denom = sum(1 for value in y_true if value == label)
        if denom == 0:
            continue
        numer = sum(1 for truth, pred in zip(y_true, y_pred, strict=False) if truth == label and pred == label)
        recalls.append(numer / denom)
    return _mean(recalls)


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return ordered[idx]


@dataclass(slots=True)
class V129BCommercialAerospaceHierarchicalStateMachinePilotReport:
    summary: dict[str, Any]
    label_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "label_rows": self.label_rows,
            "interpretation": self.interpretation,
        }


class V129BCommercialAerospaceHierarchicalStateMachinePilotAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _split_rows(self, rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        ordered_dates = sorted({row["trade_date"] for row in rows})
        split_idx = max(1, round(len(ordered_dates) * 0.8))
        train_dates = set(ordered_dates[:split_idx])
        test_dates = set(ordered_dates[split_idx:])
        train_rows = [row for row in rows if row["trade_date"] in train_dates]
        test_rows = [row for row in rows if row["trade_date"] in test_dates]
        return train_rows, test_rows

    def _standardize(self, train_rows: list[dict[str, Any]], test_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        stats: dict[str, tuple[float, float]] = {}
        for feature in NUMERIC_FEATURES:
            values = [float(row[feature]) for row in train_rows]
            mean = _mean(values)
            std = _std(values, mean)
            stats[feature] = (mean, std)

        def transform(rows_in: list[dict[str, Any]]) -> list[dict[str, Any]]:
            out: list[dict[str, Any]] = []
            for row in rows_in:
                enriched = dict(row)
                for feature in NUMERIC_FEATURES:
                    mean, std = stats[feature]
                    enriched[f"{feature}_z"] = (float(row[feature]) - mean) / std
                out.append(enriched)
            return out

        return transform(train_rows), transform(test_rows)

    def _centroid(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "numeric": {
                feature: _mean([float(row[f"{feature}_z"]) for row in rows])
                for feature in NUMERIC_FEATURES
            },
            "categorical_mode": {
                feature: Counter(row[feature] for row in rows).most_common(1)[0][0]
                for feature in CATEGORICAL_FEATURES
            },
        }

    def _score_vs_rest(self, rows: list[dict[str, Any]], positive_rows: list[dict[str, Any]], negative_rows: list[dict[str, Any]]) -> list[float]:
        pos = self._centroid(positive_rows)
        neg = self._centroid(negative_rows)
        scores: list[float] = []
        for row in rows:
            pos_dist = sum((float(row[f"{feature}_z"]) - float(pos["numeric"][feature])) ** 2 for feature in NUMERIC_FEATURES)
            neg_dist = sum((float(row[f"{feature}_z"]) - float(neg["numeric"][feature])) ** 2 for feature in NUMERIC_FEATURES)
            pos_penalty = sum(0.0 if row[feature] == pos["categorical_mode"][feature] else 0.5 for feature in CATEGORICAL_FEATURES)
            neg_penalty = sum(0.0 if row[feature] == neg["categorical_mode"][feature] else 0.5 for feature in CATEGORICAL_FEATURES)
            scores.append((neg_dist + neg_penalty) - (pos_dist + pos_penalty))
        return scores

    def _multiclass_centroids(self, train_rows: list[dict[str, Any]], labels: set[str]) -> dict[str, dict[str, Any]]:
        centroids: dict[str, dict[str, Any]] = {}
        for label in sorted(labels):
            members = [row for row in train_rows if row["supervised_action_state"] == label]
            centroids[label] = self._centroid(members)
        return centroids

    def _predict_label(self, row: dict[str, Any], centroids: dict[str, dict[str, Any]]) -> str:
        scored: list[tuple[float, str]] = []
        for label, centroid in centroids.items():
            numeric_distance = sum(
                (float(row[f"{feature}_z"]) - float(centroid["numeric"][feature])) ** 2
                for feature in NUMERIC_FEATURES
            )
            category_penalty = sum(
                0.0 if row[feature] == centroid["categorical_mode"][feature] else 0.5
                for feature in CATEGORICAL_FEATURES
            )
            scored.append((numeric_distance + category_penalty, label))
        scored.sort(key=lambda item: item[0])
        return scored[0][1]

    def analyze(self) -> V129BCommercialAerospaceHierarchicalStateMachinePilotReport:
        table = V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows
        train_rows, test_rows = self._split_rows(rows)
        train_rows_z, test_rows_z = self._standardize(train_rows, test_rows)

        high_train = [row for row in train_rows_z if row["supervised_action_state"] in {"full_pre", "full"}]
        rest_train = [row for row in train_rows_z if row["supervised_action_state"] not in {"full_pre", "full"}]
        full_pre_train = [row for row in train_rows_z if row["supervised_action_state"] == "full_pre"]
        full_train = [row for row in train_rows_z if row["supervised_action_state"] == "full"]

        if not high_train or not full_pre_train or not full_train:
            label_rows = []
            for label in sorted({row["supervised_action_state"] for row in test_rows_z}):
                label_rows.append(
                    {
                        "label": label,
                        "test_count": sum(1 for row in test_rows_z if row["supervised_action_state"] == label),
                        "recall": None,
                    }
                )

            summary = {
                "acceptance_posture": "freeze_v129b_commercial_aerospace_hierarchical_state_machine_pilot_v1",
                "train_row_count": len(train_rows_z),
                "test_row_count": len(test_rows_z),
                "label_count": len({row["supervised_action_state"] for row in rows}),
                "high_intensity_train_count": len(high_train),
                "high_intensity_test_count": sum(1 for row in test_rows_z if row["supervised_action_state"] in {"full_pre", "full"}),
                "full_pre_train_count": len(full_pre_train),
                "full_train_count": len(full_train),
                "best_high_intensity_threshold": None,
                "balanced_accuracy": None,
                "authoritative_status": "blocked_due_to_zero_train_high_intensity_support",
                "blocking_reason": "current chronology split places full_pre and full entirely in the test segment, so the hierarchical pilot cannot be lawfully trained",
            }
            interpretation = [
                "V1.29B tests a hierarchical state-machine pilot: detect high-intensity states jointly, then split them by lawful phase context.",
                "The current chronology geometry blocks the pilot because full-pre/full have zero train support; split design must be repaired before hierarchical replay pilots continue.",
            ]
            return V129BCommercialAerospaceHierarchicalStateMachinePilotReport(
                summary=summary,
                label_rows=label_rows,
                interpretation=interpretation,
            )

        train_scores = self._score_vs_rest(train_rows_z, high_train, rest_train)
        y_train = [row["supervised_action_state"] in {"full_pre", "full"} for row in train_rows_z]
        thresholds = [_quantile(train_scores, q) for q in [0.75, 0.80, 0.85, 0.90]]
        best_threshold = thresholds[0]
        best_ba = -1.0
        for threshold in thresholds:
            y_pred = [score >= threshold for score in train_scores]
            ba = _balanced_accuracy([("high" if item else "rest") for item in y_train], [("high" if item else "rest") for item in y_pred])
            if ba > best_ba:
                best_ba = ba
                best_threshold = threshold

        low_centroids = self._multiclass_centroids(train_rows_z, {"probe", "de_risk", "neutral_hold"})
        full_pre_centroid = self._centroid(full_pre_train)
        full_centroid = self._centroid(full_train)

        predictions: list[str] = []
        test_scores = self._score_vs_rest(test_rows_z, high_train, rest_train)
        for row, score in zip(test_rows_z, test_scores, strict=False):
            if score >= best_threshold:
                if row["phase_window_semantic"] == "preheat_window":
                    predictions.append("full_pre")
                elif row["phase_window_semantic"] == "impulse_window":
                    predictions.append("full")
                else:
                    # fallback to whichever high-intensity centroid is closer
                    fp_dist = sum((float(row[f"{feature}_z"]) - float(full_pre_centroid["numeric"][feature])) ** 2 for feature in NUMERIC_FEATURES)
                    f_dist = sum((float(row[f"{feature}_z"]) - float(full_centroid["numeric"][feature])) ** 2 for feature in NUMERIC_FEATURES)
                    predictions.append("full_pre" if fp_dist <= f_dist else "full")
            else:
                predictions.append(self._predict_label(row, low_centroids))

        y_test = [row["supervised_action_state"] for row in test_rows_z]
        label_rows: list[dict[str, Any]] = []
        for label in sorted(set(y_test)):
            total = sum(1 for item in y_test if item == label)
            hit = sum(1 for truth, pred in zip(y_test, predictions, strict=False) if truth == label and pred == label)
            label_rows.append(
                {
                    "label": label,
                    "test_count": total,
                    "recall": round(hit / total, 8) if total else 0.0,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v129b_commercial_aerospace_hierarchical_state_machine_pilot_v1",
            "train_row_count": len(train_rows_z),
            "test_row_count": len(test_rows_z),
            "label_count": len({row['supervised_action_state'] for row in rows}),
            "high_intensity_train_count": len(high_train),
            "high_intensity_test_count": sum(1 for row in test_rows_z if row["supervised_action_state"] in {"full_pre", "full"}),
            "best_high_intensity_threshold": round(best_threshold, 8),
            "balanced_accuracy": round(_balanced_accuracy(y_test, predictions), 8),
            "authoritative_status": "offline_hierarchical_state_machine_pilot_non_execution",
        }
        interpretation = [
            "V1.29B tests a hierarchical state-machine pilot: detect high-intensity states jointly, then split them by lawful phase context.",
            "This remains an offline audit to check whether full-pre/full can first be learned as a combined surface before replay is reopened.",
        ]
        return V129BCommercialAerospaceHierarchicalStateMachinePilotReport(
            summary=summary,
            label_rows=label_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129BCommercialAerospaceHierarchicalStateMachinePilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129BCommercialAerospaceHierarchicalStateMachinePilotAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129b_commercial_aerospace_hierarchical_state_machine_pilot_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
