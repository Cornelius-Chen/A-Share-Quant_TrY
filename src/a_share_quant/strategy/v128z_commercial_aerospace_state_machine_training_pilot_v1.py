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


@dataclass(slots=True)
class V128ZCommercialAerospaceStateMachineTrainingPilotReport:
    summary: dict[str, Any]
    label_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "label_rows": self.label_rows,
            "interpretation": self.interpretation,
        }


class V128ZCommercialAerospaceStateMachineTrainingPilotAnalyzer:
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

    def _fit_centroids(self, train_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        labels = sorted({row["supervised_action_state"] for row in train_rows})
        centroids: dict[str, dict[str, Any]] = {}
        for label in labels:
            members = [row for row in train_rows if row["supervised_action_state"] == label]
            centroids[label] = {
                "numeric": {
                    feature: _mean([float(row[f"{feature}_z"]) for row in members])
                    for feature in NUMERIC_FEATURES
                },
                "categorical_mode": {
                    feature: Counter(row[feature] for row in members).most_common(1)[0][0]
                    for feature in CATEGORICAL_FEATURES
                },
            }
        return centroids

    def _predict(self, rows: list[dict[str, Any]], centroids: dict[str, dict[str, Any]]) -> list[str]:
        predictions: list[str] = []
        for row in rows:
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
            predictions.append(scored[0][1])
        return predictions

    def analyze(self) -> V128ZCommercialAerospaceStateMachineTrainingPilotReport:
        table = V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows
        train_rows, test_rows = self._split_rows(rows)
        train_rows_z, test_rows_z = self._standardize(train_rows, test_rows)
        centroids = self._fit_centroids(train_rows_z)
        y_test = [row["supervised_action_state"] for row in test_rows_z]
        y_pred = self._predict(test_rows_z, centroids)

        label_rows: list[dict[str, Any]] = []
        for label in sorted(set(y_test)):
            total = sum(1 for item in y_test if item == label)
            hit = sum(1 for truth, pred in zip(y_test, y_pred, strict=False) if truth == label and pred == label)
            label_rows.append(
                {
                    "label": label,
                    "test_count": total,
                    "recall": round(hit / total, 8) if total else 0.0,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v128z_commercial_aerospace_state_machine_training_pilot_v1",
            "train_row_count": len(train_rows_z),
            "test_row_count": len(test_rows_z),
            "label_count": len({row['supervised_action_state'] for row in rows}),
            "model_family": "nearest_centroid_state_machine_candidate",
            "balanced_accuracy": round(_balanced_accuracy(y_test, y_pred), 8),
            "authoritative_status": "offline_state_machine_supervised_pilot_non_execution",
        }
        interpretation = [
            "V1.28Z is the first offline training pilot on the refreshed commercial-aerospace state machine.",
            "It remains a non-execution audit: the purpose is to see whether full-pre becomes a learnable middle state before any replay is re-opened.",
        ]
        return V128ZCommercialAerospaceStateMachineTrainingPilotReport(
            summary=summary,
            label_rows=label_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128ZCommercialAerospaceStateMachineTrainingPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128ZCommercialAerospaceStateMachineTrainingPilotAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128z_commercial_aerospace_state_machine_training_pilot_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
