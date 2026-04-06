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
    positives = [row for row in rows if bool(row.get("positive_close_label"))]
    negatives = [row for row in rows if not bool(row.get("positive_close_label"))]
    tp = sum(1 for row in positives if _to_float(row.get("participation_collapse_close_risk_score")) >= threshold)
    fp = sum(1 for row in negatives if _to_float(row.get("participation_collapse_close_risk_score")) >= threshold)
    tn = len(negatives) - fp
    tpr = tp / len(positives) if positives else 0.0
    tnr = tn / len(negatives) if negatives else 0.0
    return {
        "threshold": round(threshold, 6),
        "positive_recall": round(tpr, 6),
        "negative_reject_rate": round(tnr, 6),
        "balanced_accuracy": round((tpr + tnr) / 2.0, 6),
    }


@dataclass(slots=True)
class V121GCpoCloseContextSymbolHoldoutAuditReport:
    summary: dict[str, Any]
    holdout_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "holdout_rows": self.holdout_rows,
            "interpretation": self.interpretation,
        }


class V121GCpoCloseContextSymbolHoldoutAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v121e_payload: dict[str, Any]) -> V121GCpoCloseContextSymbolHoldoutAuditReport:
        rows = list(v121e_payload.get("scored_rows", []))
        symbols = sorted({str(row["symbol"]) for row in rows})
        holdout_rows: list[dict[str, Any]] = []
        for holdout_symbol in symbols:
            train_rows = [row for row in rows if str(row["symbol"]) != holdout_symbol]
            test_rows = [row for row in rows if str(row["symbol"]) == holdout_symbol]
            thresholds = sorted({_to_float(row.get("participation_collapse_close_risk_score")) for row in train_rows}, reverse=True)
            best_train = None
            for threshold in thresholds:
                record = _balanced_accuracy(train_rows, threshold)
                if best_train is None or record["balanced_accuracy"] > best_train["balanced_accuracy"]:
                    best_train = record
            best_train = best_train or {"threshold": 0.0, "balanced_accuracy": 0.0}
            test_record = _balanced_accuracy(test_rows, _to_float(best_train["threshold"]))
            holdout_rows.append(
                {
                    "holdout_symbol": holdout_symbol,
                    "train_row_count": len(train_rows),
                    "test_row_count": len(test_rows),
                    "train_positive_count": sum(1 for row in train_rows if bool(row.get("positive_close_label"))),
                    "test_positive_count": sum(1 for row in test_rows if bool(row.get("positive_close_label"))),
                    "train_best_threshold": best_train["threshold"],
                    "train_best_balanced_accuracy": best_train["balanced_accuracy"],
                    "test_balanced_accuracy": test_record["balanced_accuracy"],
                    "test_positive_recall": test_record["positive_recall"],
                    "test_negative_reject_rate": test_record["negative_reject_rate"],
                }
            )

        mean_test_balanced_accuracy = sum(_to_float(row["test_balanced_accuracy"]) for row in holdout_rows) / len(holdout_rows)
        min_test_balanced_accuracy = min(_to_float(row["test_balanced_accuracy"]) for row in holdout_rows)
        summary = {
            "acceptance_posture": "freeze_v121g_cpo_close_context_symbol_holdout_audit_v1",
            "holdout_count": len(holdout_rows),
            "mean_test_balanced_accuracy": round(mean_test_balanced_accuracy, 6),
            "min_test_balanced_accuracy": round(min_test_balanced_accuracy, 6),
            "recommended_next_posture": "send_EFG_to_adversarial_review_before_any_additional_narrowing",
        }
        interpretation = [
            "V1.21G tests whether the narrowed close-risk branch survives object transfer inside the close-only context.",
            "This matters because several earlier add-side lines died once symbol and role entanglement was exposed.",
            "A line that only works on one name should not be mistaken for a reusable close-side rule.",
        ]
        return V121GCpoCloseContextSymbolHoldoutAuditReport(
            summary=summary,
            holdout_rows=holdout_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121GCpoCloseContextSymbolHoldoutAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121GCpoCloseContextSymbolHoldoutAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v121e_payload=json.loads((repo_root / "reports" / "analysis" / "v121e_cpo_close_context_narrowing_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121g_cpo_close_context_symbol_holdout_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

