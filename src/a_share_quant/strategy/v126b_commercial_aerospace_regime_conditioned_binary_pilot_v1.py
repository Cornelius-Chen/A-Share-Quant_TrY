from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125x_commercial_aerospace_eod_binary_action_pilot_v1 import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    _balanced_accuracy_binary,
    _mean,
    _std,
)
from a_share_quant.strategy.v126a_commercial_aerospace_regime_conditioned_label_table_v1 import (
    V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer,
)


TASKS = {
    "eligibility_binary_rc": {"positive": {"probe_eligibility_target", "full_eligibility_target"}},
    "de_risk_binary_rc": {"positive": {"de_risk_target"}},
}


@dataclass(slots=True)
class V126BCommercialAerospaceRegimeConditionedBinaryPilotReport:
    summary: dict[str, Any]
    task_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "task_rows": self.task_rows,
            "interpretation": self.interpretation,
        }


class V126BCommercialAerospaceRegimeConditionedBinaryPilotAnalyzer:
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
        positives = [row for row in train_rows if row["supervised_action_label_rc"] in positive_labels]
        negatives = [row for row in train_rows if row["supervised_action_label_rc"] not in positive_labels]
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

    def analyze(self) -> V126BCommercialAerospaceRegimeConditionedBinaryPilotReport:
        table = V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows
        train_rows, test_rows = self._split_rows(rows)
        train_rows_z, test_rows_z = self._standardize(train_rows, test_rows)
        task_rows: list[dict[str, Any]] = []
        for task_name, config in TASKS.items():
            train_scores = self._score_rows(train_rows_z, train_rows_z, config["positive"])
            test_scores = self._score_rows(train_rows_z, test_rows_z, config["positive"])
            y_train = [1 if row["supervised_action_label_rc"] in config["positive"] else 0 for row in train_rows_z]
            y_test = [1 if row["supervised_action_label_rc"] in config["positive"] else 0 for row in test_rows_z]
            threshold, train_ba = self._best_threshold(train_scores, y_train)
            y_pred = [1 if score >= threshold else 0 for score in test_scores]
            test_ba = _balanced_accuracy_binary(y_test, y_pred)
            task_rows.append(
                {
                    "task_name": task_name,
                    "train_positive_count": sum(y_train),
                    "test_positive_count": sum(y_test),
                    "train_balanced_accuracy": round(train_ba, 8),
                    "test_balanced_accuracy": round(test_ba, 8),
                }
            )

        best_task = max(task_rows, key=lambda row: row["test_balanced_accuracy"])
        summary = {
            "acceptance_posture": "freeze_v126b_commercial_aerospace_regime_conditioned_binary_pilot_v1",
            "train_row_count": len(train_rows_z),
            "test_row_count": len(test_rows_z),
            "best_task_name": best_task["task_name"],
            "best_test_balanced_accuracy": best_task["test_balanced_accuracy"],
            "authoritative_status": "regime_conditioned_lawful_eod_binary_pilot_non_execution",
        }
        interpretation = [
            "V1.26B reruns binary action learning after replacing global labels with regime-conditioned labels.",
            "This is the direct test of whether the replay blocker was label geometry rather than signal content.",
        ]
        return V126BCommercialAerospaceRegimeConditionedBinaryPilotReport(
            summary=summary,
            task_rows=task_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V126BCommercialAerospaceRegimeConditionedBinaryPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126BCommercialAerospaceRegimeConditionedBinaryPilotAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126b_commercial_aerospace_regime_conditioned_binary_pilot_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
