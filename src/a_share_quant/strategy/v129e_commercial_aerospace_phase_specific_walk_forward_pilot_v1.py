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

PILOT_FOLDS = [
    {
        "fold_name": "full_pre_dedicated_fold",
        "target_state": "full_pre",
        "train_start": "20240129",
        "train_end": "20251211",
        "test_start": "20251212",
        "test_end": "20251223",
    },
    {
        "fold_name": "full_dedicated_fold",
        "target_state": "full",
        "train_start": "20240129",
        "train_end": "20260106",
        "test_start": "20260107",
        "test_end": "20260112",
    },
]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: list[float], mean: float) -> float:
    if not values:
        return 1.0
    var = sum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(var) or 1.0


def _balanced_accuracy_binary(y_true: list[bool], y_pred: list[bool]) -> float:
    pos_total = sum(1 for value in y_true if value)
    neg_total = sum(1 for value in y_true if not value)
    pos_recall = sum(1 for truth, pred in zip(y_true, y_pred, strict=False) if truth and pred) / pos_total if pos_total else 0.0
    neg_recall = sum(1 for truth, pred in zip(y_true, y_pred, strict=False) if (not truth) and (not pred)) / neg_total if neg_total else 0.0
    return (pos_recall + neg_recall) / 2.0


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return ordered[idx]


@dataclass(slots=True)
class V129ECommercialAerospacePhaseSpecificWalkForwardPilotReport:
    summary: dict[str, Any]
    fold_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "fold_rows": self.fold_rows,
            "interpretation": self.interpretation,
        }


class V129ECommercialAerospacePhaseSpecificWalkForwardPilotAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

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

    def analyze(self) -> V129ECommercialAerospacePhaseSpecificWalkForwardPilotReport:
        table = V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows

        fold_rows: list[dict[str, Any]] = []
        for fold in PILOT_FOLDS:
            train_rows = [
                dict(row)
                for row in rows
                if fold["train_start"] <= row["trade_date"] <= fold["train_end"]
            ]
            test_rows = [
                dict(row)
                for row in rows
                if fold["test_start"] <= row["trade_date"] <= fold["test_end"]
            ]
            train_rows_z, test_rows_z = self._standardize(train_rows, test_rows)

            positive_train = [row for row in train_rows_z if row["supervised_action_state"] == fold["target_state"]]
            negative_train = [row for row in train_rows_z if row["supervised_action_state"] != fold["target_state"]]
            positive_test = [row for row in test_rows_z if row["supervised_action_state"] == fold["target_state"]]

            train_scores = self._score_vs_rest(train_rows_z, positive_train, negative_train)
            test_scores = self._score_vs_rest(test_rows_z, positive_train, negative_train)
            y_train = [row["supervised_action_state"] == fold["target_state"] for row in train_rows_z]
            y_test = [row["supervised_action_state"] == fold["target_state"] for row in test_rows_z]

            best_threshold = 0.0
            best_train_ba = -1.0
            for q in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
                threshold = _quantile(train_scores, q)
                y_pred = [score >= threshold for score in train_scores]
                ba = _balanced_accuracy_binary(y_train, y_pred)
                if ba > best_train_ba:
                    best_train_ba = ba
                    best_threshold = threshold

            y_test_pred = [score >= best_threshold for score in test_scores]
            tp = sum(1 for truth, pred in zip(y_test, y_test_pred, strict=False) if truth and pred)
            fp = sum(1 for truth, pred in zip(y_test, y_test_pred, strict=False) if (not truth) and pred)
            fold_rows.append(
                {
                    "fold_name": fold["fold_name"],
                    "target_state": fold["target_state"],
                    "train_positive_count": len(positive_train),
                    "test_positive_count": len(positive_test),
                    "best_train_threshold": round(best_threshold, 8),
                    "train_balanced_accuracy": round(best_train_ba, 8),
                    "test_balanced_accuracy": round(_balanced_accuracy_binary(y_test, y_test_pred), 8),
                    "test_positive_recall": round(tp / len(positive_test), 8) if positive_test else 0.0,
                    "test_positive_precision": round(tp / (tp + fp), 8) if (tp + fp) else 0.0,
                }
            )

        full_pre_row = next(row for row in fold_rows if row["target_state"] == "full_pre")
        full_row = next(row for row in fold_rows if row["target_state"] == "full")
        summary = {
            "acceptance_posture": "freeze_v129e_commercial_aerospace_phase_specific_walk_forward_pilot_v1",
            "fold_count": len(fold_rows),
            "full_pre_test_balanced_accuracy": full_pre_row["test_balanced_accuracy"],
            "full_pre_test_positive_recall": full_pre_row["test_positive_recall"],
            "full_test_balanced_accuracy": full_row["test_balanced_accuracy"],
            "full_test_positive_recall": full_row["test_positive_recall"],
            "authoritative_status": "full_pre_partial_learnability_but_full_still_too_thin",
            "authoritative_rule": "commercial-aerospace phase-specific supervision may continue for full_pre, but full should remain phase-contextual until a thicker lawful fold exists",
        }
        interpretation = [
            "V1.29E runs the smallest lawful phase-specific walk-forward pilots instead of forcing one global multiclass classifier.",
            "The goal is not replay promotion; it is to check whether any high-intensity state is learnable under a lawful fold before more tuning is attempted.",
        ]
        return V129ECommercialAerospacePhaseSpecificWalkForwardPilotReport(
            summary=summary,
            fold_rows=fold_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129ECommercialAerospacePhaseSpecificWalkForwardPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129ECommercialAerospacePhaseSpecificWalkForwardPilotAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129e_commercial_aerospace_phase_specific_walk_forward_pilot_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
