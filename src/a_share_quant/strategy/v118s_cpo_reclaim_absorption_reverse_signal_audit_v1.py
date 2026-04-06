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
    negatives = [row for row in rows if bool(row.get("negative_add_label"))]
    positives = [row for row in rows if not bool(row.get("negative_add_label"))]
    tp = sum(1 for row in negatives if _to_float(row.get("reverse_score")) >= threshold)
    fn = len(negatives) - tp
    fp = sum(1 for row in positives if _to_float(row.get("reverse_score")) >= threshold)
    tn = len(positives) - fp
    tpr = tp / len(negatives) if negatives else 0.0
    tnr = tn / len(positives) if positives else 0.0
    return {
        "threshold": round(threshold, 6),
        "negative_recall": round(tpr, 6),
        "positive_reject_rate": round(tnr, 6),
        "balanced_accuracy": round((tpr + tnr) / 2.0, 6),
    }


@dataclass(slots=True)
class V118SCpoReclaimAbsorptionReverseSignalAuditReport:
    summary: dict[str, Any]
    threshold_rows: list[dict[str, Any]]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_rows": self.threshold_rows,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


class V118SCpoReclaimAbsorptionReverseSignalAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v118o_payload: dict[str, Any]) -> V118SCpoReclaimAbsorptionReverseSignalAuditReport:
        rows = []
        for row in list(v118o_payload.get("candidate_score_rows", [])):
            enriched = dict(row)
            enriched["negative_add_label"] = not bool(row.get("positive_add_label"))
            enriched["reverse_score"] = -_to_float(row.get("reclaim_absorption_score"))
            rows.append(enriched)

        negative_rows = [row for row in rows if bool(row.get("negative_add_label"))]
        positive_rows = [row for row in rows if not bool(row.get("negative_add_label"))]
        thresholds = sorted({_to_float(row.get("reverse_score")) for row in rows}, reverse=True)

        threshold_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for threshold in thresholds:
            record = _balanced_accuracy(rows, threshold)
            threshold_rows.append(record)
            if best_row is None or record["balanced_accuracy"] > best_row["balanced_accuracy"]:
                best_row = record

        split_defs = (
            ("holdout_2023", {"2023"}),
            ("holdout_2024", {"2024"}),
            ("holdout_2025_plus", {"2025", "2026"}),
        )
        split_rows: list[dict[str, Any]] = []
        for split_name, holdout_years in split_defs:
            train_rows = [row for row in rows if str(row["signal_trade_date"])[:4] not in holdout_years]
            test_rows = [row for row in rows if str(row["signal_trade_date"])[:4] in holdout_years]
            train_thresholds = sorted({_to_float(row.get("reverse_score")) for row in train_rows}, reverse=True)
            best_train = None
            for threshold in train_thresholds:
                record = _balanced_accuracy(train_rows, threshold)
                if best_train is None or record["balanced_accuracy"] > best_train["balanced_accuracy"]:
                    best_train = record
            best_train = best_train or {"threshold": 0.0, "balanced_accuracy": 0.0}
            test_record = _balanced_accuracy(test_rows, _to_float(best_train["threshold"]))
            split_rows.append(
                {
                    "split_name": split_name,
                    "holdout_years": sorted(holdout_years),
                    "train_best_threshold": best_train["threshold"],
                    "train_best_balanced_accuracy": best_train["balanced_accuracy"],
                    "test_balanced_accuracy": test_record["balanced_accuracy"],
                    "test_negative_recall": test_record["negative_recall"],
                    "test_positive_reject_rate": test_record["positive_reject_rate"],
                }
            )

        negative_mean = sum(_to_float(row.get("reverse_score")) for row in negative_rows) / len(negative_rows)
        positive_mean = sum(_to_float(row.get("reverse_score")) for row in positive_rows) / len(positive_rows)
        mean_test = sum(_to_float(row["test_balanced_accuracy"]) for row in split_rows) / len(split_rows)
        min_test = min(_to_float(row["test_balanced_accuracy"]) for row in split_rows)

        summary = {
            "acceptance_posture": "freeze_v118s_cpo_reclaim_absorption_reverse_signal_audit_v1",
            "source_branch": "reclaim_absorption_score_candidate",
            "reverse_signal_status": (
                "candidate_reverse_soft_component"
                if (negative_mean > positive_mean and min_test >= 0.5)
                else "not_stable_reverse_signal"
            ),
            "negative_mean_reverse_score": round(negative_mean, 6),
            "positive_mean_reverse_score": round(positive_mean, 6),
            "reverse_gap_negative_minus_positive": round(negative_mean - positive_mean, 6),
            "best_balanced_accuracy": best_row["balanced_accuracy"] if best_row else 0.0,
            "mean_test_balanced_accuracy": round(mean_test, 6),
            "min_test_balanced_accuracy": round(min_test, 6),
            "recommended_next_posture": (
                "keep_only_as_reverse_soft_component"
                if (negative_mean > positive_mean and min_test >= 0.5)
                else "do_not_rescue_reclaim_absorption_as_reverse_signal"
            ),
        }
        interpretation = [
            "V1.18S checks the user's reverse-indicator hypothesis directly: if the forward branch is wrong, is it at least stable when inverted?",
            "The audit inverts the reclaim-absorption score and tests whether negative add rows are ranked above positive ones, then applies the same crude year-split discipline.",
            "A reverse branch only deserves rescue if it is both directionally correct and chronology-stable; otherwise it should die cleanly.",
        ]
        return V118SCpoReclaimAbsorptionReverseSignalAuditReport(
            summary=summary,
            threshold_rows=threshold_rows,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118SCpoReclaimAbsorptionReverseSignalAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V118SCpoReclaimAbsorptionReverseSignalAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v118o_payload=json.loads((repo_root / "reports" / "analysis" / "v118o_cpo_reclaim_absorption_discovery_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118s_cpo_reclaim_absorption_reverse_signal_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
