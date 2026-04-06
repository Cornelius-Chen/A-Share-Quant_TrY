from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125x_commercial_aerospace_eod_binary_action_pilot_v1 import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
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

QUANTILES = [0.2, 0.3, 0.4, 0.6, 0.7, 0.8]


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return ordered[idx]


@dataclass(slots=True)
class V126DCommercialAerospaceScoreDirectionAuditReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V126DCommercialAerospaceScoreDirectionAuditAnalyzer:
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

    def analyze(self) -> V126DCommercialAerospaceScoreDirectionAuditReport:
        table = V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows
        train_rows, test_rows = self._split_rows(rows)
        train_rows_z, test_rows_z = self._standardize(train_rows, test_rows)
        direction_rows: list[dict[str, Any]] = []
        for task_name, config in TASKS.items():
            train_scores = self._score_rows(train_rows_z, train_rows_z, config["positive"])
            test_scores = self._score_rows(train_rows_z, test_rows_z, config["positive"])
            for direction in ("high_pass", "low_pass"):
                for q in QUANTILES:
                    threshold = _quantile(train_scores, q)
                    if direction == "high_pass":
                        passed = [row for row, score in zip(test_rows_z, test_scores, strict=False) if score >= threshold]
                        failed = [row for row, score in zip(test_rows_z, test_scores, strict=False) if score < threshold]
                    else:
                        passed = [row for row, score in zip(test_rows_z, test_scores, strict=False) if score <= threshold]
                        failed = [row for row, score in zip(test_rows_z, test_scores, strict=False) if score > threshold]
                    pass_mean = _mean([float(row["forward_return_10"]) for row in passed])
                    fail_mean = _mean([float(row["forward_return_10"]) for row in failed])
                    if "eligibility" in task_name:
                        economic_spread = pass_mean - fail_mean
                    else:
                        economic_spread = fail_mean - pass_mean
                    direction_rows.append(
                        {
                            "task_name": task_name,
                            "direction": direction,
                            "threshold_quantile": q,
                            "pass_count": len(passed),
                            "pass_rate": round(len(passed) / len(test_rows_z), 8) if test_rows_z else 0.0,
                            "pass_forward_mean": round(pass_mean, 8),
                            "fail_forward_mean": round(fail_mean, 8),
                            "economic_spread": round(economic_spread, 8),
                        }
                    )

        best_rows: dict[str, dict[str, Any]] = {}
        for row in direction_rows:
            best_rows.setdefault(row["task_name"], row)
            if row["economic_spread"] > best_rows[row["task_name"]]["economic_spread"]:
                best_rows[row["task_name"]] = row

        summary = {
            "acceptance_posture": "freeze_v126d_commercial_aerospace_score_direction_audit_v1",
            "best_eligibility_direction": best_rows["eligibility_binary_rc"]["direction"],
            "best_eligibility_spread": best_rows["eligibility_binary_rc"]["economic_spread"],
            "best_de_risk_direction": best_rows["de_risk_binary_rc"]["direction"],
            "best_de_risk_spread": best_rows["de_risk_binary_rc"]["economic_spread"],
            "authoritative_status": "score_direction_audit_non_execution",
        }
        interpretation = [
            "V1.26D checks whether the lawful EOD score is directionally inverted, which can happen when label geometry and class imbalance diverge.",
            "This decides whether replay is blocked by missing signal or just by wrong score orientation.",
        ]
        return V126DCommercialAerospaceScoreDirectionAuditReport(
            summary=summary,
            direction_rows=direction_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V126DCommercialAerospaceScoreDirectionAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126DCommercialAerospaceScoreDirectionAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126d_commercial_aerospace_score_direction_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
