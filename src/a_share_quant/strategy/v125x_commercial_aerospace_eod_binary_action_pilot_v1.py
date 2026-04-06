from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125t_commercial_aerospace_lawful_supervised_action_training_table_v1 import (
    V125TCommercialAerospaceLawfulSupervisedActionTrainingTableAnalyzer,
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

CATEGORICAL_FEATURES = ["regime_proxy_semantic", "event_state"]

TASKS = {
    "eligibility_binary": {"positive": {"probe_eligibility_target", "full_eligibility_target"}},
    "de_risk_binary": {"positive": {"de_risk_target"}},
}


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: list[float], mean: float) -> float:
    if not values:
        return 1.0
    var = sum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(var) or 1.0


def _balanced_accuracy_binary(y_true: list[int], y_pred: list[int]) -> float:
    pos_total = sum(1 for value in y_true if value == 1)
    neg_total = sum(1 for value in y_true if value == 0)
    pos_recall = sum(1 for truth, pred in zip(y_true, y_pred, strict=False) if truth == 1 and pred == 1) / pos_total if pos_total else 0.0
    neg_recall = sum(1 for truth, pred in zip(y_true, y_pred, strict=False) if truth == 0 and pred == 0) / neg_total if neg_total else 0.0
    return 0.5 * (pos_recall + neg_recall)


@dataclass(slots=True)
class V125XCommercialAerospaceEODBinaryActionPilotReport:
    summary: dict[str, Any]
    task_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "task_rows": self.task_rows,
            "interpretation": self.interpretation,
        }


class V125XCommercialAerospaceEODBinaryActionPilotAnalyzer:
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

    def _score_rows(self, train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]], positive_labels: set[str]) -> list[float]:
        positives = [row for row in train_rows if row["supervised_action_label"] in positive_labels]
        negatives = [row for row in train_rows if row["supervised_action_label"] not in positive_labels]
        pos_numeric = {feature: _mean([float(row[f"{feature}_z"]) for row in positives]) for feature in NUMERIC_FEATURES}
        neg_numeric = {feature: _mean([float(row[f"{feature}_z"]) for row in negatives]) for feature in NUMERIC_FEATURES}
        pos_cat = {
            feature: max(
                {value for value in (row[feature] for row in positives)},
                key=lambda candidate: sum(1 for row in positives if row[feature] == candidate),
            )
            for feature in CATEGORICAL_FEATURES
        }
        neg_cat = {
            feature: max(
                {value for value in (row[feature] for row in negatives)},
                key=lambda candidate: sum(1 for row in negatives if row[feature] == candidate),
            )
            for feature in CATEGORICAL_FEATURES
        }

        scores: list[float] = []
        for row in eval_rows:
            numeric_score = sum(
                abs(float(row[f"{feature}_z"]) - neg_numeric[feature]) - abs(float(row[f"{feature}_z"]) - pos_numeric[feature])
                for feature in NUMERIC_FEATURES
            )
            cat_score = sum(
                (0.5 if row[feature] == pos_cat[feature] else 0.0) - (0.5 if row[feature] == neg_cat[feature] else 0.0)
                for feature in CATEGORICAL_FEATURES
            )
            scores.append(numeric_score + cat_score)
        return scores

    def _best_threshold(self, scores: list[float], labels: list[int]) -> tuple[float, float]:
        candidates = sorted(set(scores))
        best_threshold = 0.0
        best_ba = -1.0
        for threshold in candidates:
            preds = [1 if score >= threshold else 0 for score in scores]
            ba = _balanced_accuracy_binary(labels, preds)
            if ba > best_ba:
                best_ba = ba
                best_threshold = threshold
        return best_threshold, best_ba

    def analyze(self) -> V125XCommercialAerospaceEODBinaryActionPilotReport:
        table = V125TCommercialAerospaceLawfulSupervisedActionTrainingTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows
        train_rows, test_rows = self._split_rows(rows)
        train_rows_z, test_rows_z = self._standardize(train_rows, test_rows)

        task_rows: list[dict[str, Any]] = []
        for task_name, config in TASKS.items():
            positive_labels = config["positive"]
            train_scores = self._score_rows(train_rows_z, train_rows_z, positive_labels)
            test_scores = self._score_rows(train_rows_z, test_rows_z, positive_labels)
            y_train = [1 if row["supervised_action_label"] in positive_labels else 0 for row in train_rows_z]
            y_test = [1 if row["supervised_action_label"] in positive_labels else 0 for row in test_rows_z]
            threshold, train_ba = self._best_threshold(train_scores, y_train)
            y_pred = [1 if score >= threshold else 0 for score in test_scores]
            test_ba = _balanced_accuracy_binary(y_test, y_pred)
            pos_total = sum(y_test)
            neg_total = len(y_test) - pos_total
            pos_recall = sum(1 for truth, pred in zip(y_test, y_pred, strict=False) if truth == 1 and pred == 1) / pos_total if pos_total else 0.0
            neg_recall = sum(1 for truth, pred in zip(y_test, y_pred, strict=False) if truth == 0 and pred == 0) / neg_total if neg_total else 0.0
            task_rows.append(
                {
                    "task_name": task_name,
                    "train_positive_count": sum(y_train),
                    "test_positive_count": pos_total,
                    "selected_threshold": round(threshold, 8),
                    "train_balanced_accuracy": round(train_ba, 8),
                    "test_balanced_accuracy": round(test_ba, 8),
                    "test_positive_recall": round(pos_recall, 8),
                    "test_negative_recall": round(neg_recall, 8),
                }
            )

        best_task = max(task_rows, key=lambda row: row["test_balanced_accuracy"])
        summary = {
            "acceptance_posture": "freeze_v125x_commercial_aerospace_eod_binary_action_pilot_v1",
            "train_row_count": len(train_rows_z),
            "test_row_count": len(test_rows_z),
            "task_count": len(task_rows),
            "best_task_name": best_task["task_name"],
            "best_test_balanced_accuracy": best_task["test_balanced_accuracy"],
            "authoritative_status": "lawful_eod_binary_action_learning_pilot_non_execution",
        }
        interpretation = [
            "V1.25X compresses the lawful EOD supervised table into binary execution-adjacent tasks that are closer to replay semantics than the original 4-class pilot.",
            "This remains an offline training audit and not yet a replay rule.",
        ]
        return V125XCommercialAerospaceEODBinaryActionPilotReport(
            summary=summary,
            task_rows=task_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125XCommercialAerospaceEODBinaryActionPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125XCommercialAerospaceEODBinaryActionPilotAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125x_commercial_aerospace_eod_binary_action_pilot_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
