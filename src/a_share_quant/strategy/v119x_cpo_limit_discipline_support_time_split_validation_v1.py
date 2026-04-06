from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _balanced_accuracy(rows: list[dict[str, Any]], threshold: float) -> dict[str, float]:
    tp = sum(bool(row["positive_add_label"]) and _to_float(row["limit_discipline_support_score"]) >= threshold for row in rows)
    fn = sum(bool(row["positive_add_label"]) and _to_float(row["limit_discipline_support_score"]) < threshold for row in rows)
    fp = sum((not bool(row["positive_add_label"])) and _to_float(row["limit_discipline_support_score"]) >= threshold for row in rows)
    tn = sum((not bool(row["positive_add_label"])) and _to_float(row["limit_discipline_support_score"]) < threshold for row in rows)
    positive_recall = tp / (tp + fn) if (tp + fn) else 0.0
    negative_reject_rate = tn / (tn + fp) if (tn + fp) else 0.0
    return {
        "balanced_accuracy": (positive_recall + negative_reject_rate) / 2.0,
        "positive_recall": positive_recall,
        "negative_reject_rate": negative_reject_rate,
    }


@dataclass(slots=True)
class V119XCpoLimitDisciplineSupportTimeSplitValidationReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "split_rows": self.split_rows, "interpretation": self.interpretation}


class V119XCpoLimitDisciplineSupportTimeSplitValidationAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v119v_payload: dict[str, Any],
        v119n_payload: dict[str, Any],
    ) -> V119XCpoLimitDisciplineSupportTimeSplitValidationReport:
        rows = v119v_payload["candidate_score_rows"]
        split_definitions = [
            ("holdout_2023", {"2023"}),
            ("holdout_2024", {"2024"}),
            ("holdout_2025_plus", {"2025", "2026"}),
        ]
        split_rows: list[dict[str, Any]] = []
        for split_name, holdout_years in split_definitions:
            train_rows = [row for row in rows if str(row["signal_trade_date"])[:4] not in holdout_years]
            test_rows = [row for row in rows if str(row["signal_trade_date"])[:4] in holdout_years]
            train_thresholds = sorted(
                {_to_float(row["limit_discipline_support_score"]) for row in train_rows},
                reverse=True,
            )
            best_threshold = train_thresholds[0]
            best_bal_acc = -1.0
            for threshold in train_thresholds:
                metrics = _balanced_accuracy(train_rows, threshold)
                if metrics["balanced_accuracy"] > best_bal_acc:
                    best_bal_acc = metrics["balanced_accuracy"]
                    best_threshold = threshold
            test_metrics = _balanced_accuracy(test_rows, best_threshold)
            split_rows.append(
                {
                    "split_name": split_name,
                    "holdout_years": sorted(holdout_years),
                    "train_row_count": len(train_rows),
                    "test_row_count": len(test_rows),
                    "train_positive_count": sum(bool(row["positive_add_label"]) for row in train_rows),
                    "test_positive_count": sum(bool(row["positive_add_label"]) for row in test_rows),
                    "train_best_threshold": round(best_threshold, 6),
                    "train_best_balanced_accuracy": round(best_bal_acc, 6),
                    "test_balanced_accuracy": round(test_metrics["balanced_accuracy"], 6),
                    "test_positive_recall": round(test_metrics["positive_recall"], 6),
                    "test_negative_reject_rate": round(test_metrics["negative_reject_rate"], 6),
                }
            )
        mean_test_balanced_accuracy = sum(_to_float(row["test_balanced_accuracy"]) for row in split_rows) / len(split_rows)
        min_test_balanced_accuracy = min(_to_float(row["test_balanced_accuracy"]) for row in split_rows)
        summary = {
            "acceptance_posture": "freeze_v119x_cpo_limit_discipline_support_time_split_validation_v1",
            "split_count": len(split_rows),
            "mean_test_balanced_accuracy": round(mean_test_balanced_accuracy, 6),
            "min_test_balanced_accuracy": round(min_test_balanced_accuracy, 6),
            "parent_mean_test_balanced_accuracy": v119n_payload["summary"]["mean_test_balanced_accuracy"],
            "parent_min_test_balanced_accuracy": v119n_payload["summary"]["min_test_balanced_accuracy"],
            "time_split_increment_vs_parent": round(
                mean_test_balanced_accuracy - _to_float(v119n_payload["summary"]["mean_test_balanced_accuracy"]),
                6,
            ),
            "stability_posture": (
                "candidate_stable_enough_for_triage"
                if min_test_balanced_accuracy >= 0.5
                else "candidate_unstable_under_time_split"
            ),
            "recommended_next_posture": "send_VWX_to_three_run_adversarial_review_then_kill_or_keep_fast",
        }
        interpretation = [
            "V1.19X asks the only chronology question that matters here: does limit-band discipline actually help across years, especially the difficult 2024 slice?",
            "This branch should not survive just because the external surface ties; it must also avoid making chronology worse.",
            "The result here closes the three-run block and should trigger an immediate kill-or-keep decision.",
        ]
        return V119XCpoLimitDisciplineSupportTimeSplitValidationReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V119XCpoLimitDisciplineSupportTimeSplitValidationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119XCpoLimitDisciplineSupportTimeSplitValidationAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v119v_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v119v_cpo_limit_discipline_support_discovery_v1.json").read_text(
                encoding="utf-8"
            )
        ),
        v119n_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v119n_cpo_participation_turnover_elg_support_time_split_validation_v1.json").read_text(
                encoding="utf-8"
            )
        ),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119x_cpo_limit_discipline_support_time_split_validation_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
