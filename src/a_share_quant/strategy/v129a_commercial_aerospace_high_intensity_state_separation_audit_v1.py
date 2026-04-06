from __future__ import annotations

import json
import math
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
class V129ACommercialAerospaceHighIntensityStateSeparationAuditReport:
    summary: dict[str, Any]
    audit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "audit_rows": self.audit_rows,
            "interpretation": self.interpretation,
        }


class V129ACommercialAerospaceHighIntensityStateSeparationAuditAnalyzer:
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
                feature: max({row[feature] for row in rows}, key=lambda key: sum(1 for row in rows if row[feature] == key))
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

    def _best_threshold(self, scores: list[float], y_true: list[bool]) -> tuple[float, float]:
        best_threshold = 0.0
        best_ba = -1.0
        for q in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
            threshold = _quantile(scores, q)
            y_pred = [score >= threshold for score in scores]
            ba = _balanced_accuracy_binary(y_true, y_pred)
            if ba > best_ba:
                best_ba = ba
                best_threshold = threshold
        return best_threshold, best_ba

    def analyze(self) -> V129ACommercialAerospaceHighIntensityStateSeparationAuditReport:
        table = V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows
        train_rows, test_rows = self._split_rows(rows)
        train_rows_z, test_rows_z = self._standardize(train_rows, test_rows)

        definitions = [
            ("high_intensity", lambda row: row["supervised_action_state"] in {"full_pre", "full"}),
            ("full_pre_vs_rest", lambda row: row["supervised_action_state"] == "full_pre"),
            ("full_vs_rest", lambda row: row["supervised_action_state"] == "full"),
        ]

        audit_rows: list[dict[str, Any]] = []
        blocked_targets: list[str] = []
        for name, matcher in definitions:
            positive_train = [row for row in train_rows_z if matcher(row)]
            negative_train = [row for row in train_rows_z if not matcher(row)]
            positive_test = [row for row in test_rows_z if matcher(row)]
            if not positive_train:
                blocked_targets.append(name)
                audit_rows.append(
                    {
                        "target": name,
                        "train_positive_count": 0,
                        "test_positive_count": len(positive_test),
                        "evaluable": False,
                        "blocking_reason": "zero_train_positive_support_under_current_chronology_split",
                        "best_train_threshold": None,
                        "train_balanced_accuracy": None,
                        "test_balanced_accuracy": None,
                        "test_positive_recall": None,
                    }
                )
                continue

            train_scores = self._score_vs_rest(train_rows_z, positive_train, negative_train)
            test_scores = self._score_vs_rest(test_rows_z, positive_train, negative_train)
            y_train = [matcher(row) for row in train_rows_z]
            y_test = [matcher(row) for row in test_rows_z]
            threshold, train_ba = self._best_threshold(train_scores, y_train)
            y_test_pred = [score >= threshold for score in test_scores]
            test_ba = _balanced_accuracy_binary(y_test, y_test_pred)
            pos_total = len(positive_test)
            pos_recall = sum(1 for truth, pred in zip(y_test, y_test_pred, strict=False) if truth and pred) / pos_total if pos_total else 0.0
            audit_rows.append(
                {
                    "target": name,
                    "train_positive_count": len(positive_train),
                    "test_positive_count": len(positive_test),
                    "evaluable": True,
                    "blocking_reason": None,
                    "best_train_threshold": round(threshold, 8),
                    "train_balanced_accuracy": round(train_ba, 8),
                    "test_balanced_accuracy": round(test_ba, 8),
                    "test_positive_recall": round(pos_recall, 8),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v129a_commercial_aerospace_high_intensity_state_separation_audit_v1",
            "row_count": len(rows),
            "train_row_count": len(train_rows_z),
            "test_row_count": len(test_rows_z),
            "blocked_target_count": len(blocked_targets),
            "blocked_targets": blocked_targets,
            "authoritative_status": (
                "blocked_due_to_zero_train_high_intensity_support"
                if blocked_targets
                else "evaluable_non_execution_audit"
            ),
            "authoritative_rule": "before replay reopens the commercial-aerospace state machine should prove that high-intensity states are at least jointly separable from the rest of the state surface",
        }
        interpretation = [
            "V1.29A audits whether full-pre and full can first be recognized as a combined high-intensity surface before trying to predict them separately.",
            "If high-intensity targets have zero train support under the current chronology split, separation is blocked and split geometry must be reworked before classifier tuning continues.",
        ]
        return V129ACommercialAerospaceHighIntensityStateSeparationAuditReport(
            summary=summary,
            audit_rows=audit_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129ACommercialAerospaceHighIntensityStateSeparationAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129ACommercialAerospaceHighIntensityStateSeparationAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129a_commercial_aerospace_high_intensity_state_separation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
