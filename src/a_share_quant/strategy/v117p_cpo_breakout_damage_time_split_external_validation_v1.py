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
    positives = [row for row in rows if bool(row.get("positive_add_label"))]
    negatives = [row for row in rows if not bool(row.get("positive_add_label"))]
    tp = sum(1 for row in positives if _to_float(row.get("candidate_damage_score")) >= threshold)
    fn = len(positives) - tp
    fp = sum(1 for row in negatives if _to_float(row.get("candidate_damage_score")) >= threshold)
    tn = len(negatives) - fp
    tpr = tp / len(positives) if positives else 0.0
    tnr = tn / len(negatives) if negatives else 0.0
    return {
        "threshold": round(threshold, 6),
        "tp": tp,
        "fn": fn,
        "fp": fp,
        "tn": tn,
        "positive_recall": round(tpr, 6),
        "negative_reject_rate": round(tnr, 6),
        "balanced_accuracy": round((tpr + tnr) / 2.0, 6),
    }


@dataclass(slots=True)
class V117PCpoBreakoutDamageTimeSplitExternalValidationReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


class V117PCpoBreakoutDamageTimeSplitExternalValidationAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v117o_payload: dict[str, Any]) -> V117PCpoBreakoutDamageTimeSplitExternalValidationReport:
        all_rows = [
            dict(row)
            for row in list(v117o_payload.get("external_pool_rows", []))
            if str(row.get("action_context")) == "add_vs_hold"
        ]

        def train_best_threshold(train_rows: list[dict[str, Any]]) -> dict[str, Any]:
            thresholds = sorted({_to_float(row.get("candidate_damage_score")) for row in train_rows}, reverse=True)
            best: dict[str, Any] | None = None
            for threshold in thresholds:
                metrics = _balanced_accuracy(train_rows, threshold)
                if best is None or metrics["balanced_accuracy"] > best["balanced_accuracy"]:
                    best = metrics
            return best or {"threshold": 0.0, "balanced_accuracy": 0.0}

        split_defs = (
            ("holdout_2023", {"2023"}),
            ("holdout_2024", {"2024"}),
            ("holdout_2025_plus", {"2025", "2026"}),
        )

        split_rows: list[dict[str, Any]] = []
        for split_name, holdout_years in split_defs:
            train_rows = [row for row in all_rows if str(row["signal_trade_date"])[:4] not in holdout_years]
            test_rows = [row for row in all_rows if str(row["signal_trade_date"])[:4] in holdout_years]
            train_best = train_best_threshold(train_rows)
            test_metrics = _balanced_accuracy(test_rows, _to_float(train_best["threshold"]))
            split_rows.append(
                {
                    "split_name": split_name,
                    "holdout_years": sorted(holdout_years),
                    "train_row_count": len(train_rows),
                    "test_row_count": len(test_rows),
                    "train_positive_count": sum(1 for row in train_rows if bool(row.get("positive_add_label"))),
                    "test_positive_count": sum(1 for row in test_rows if bool(row.get("positive_add_label"))),
                    "train_best_threshold": train_best["threshold"],
                    "train_best_balanced_accuracy": train_best["balanced_accuracy"],
                    "test_balanced_accuracy": test_metrics["balanced_accuracy"],
                    "test_positive_recall": test_metrics["positive_recall"],
                    "test_negative_reject_rate": test_metrics["negative_reject_rate"],
                }
            )

        mean_test_balanced_accuracy = sum(_to_float(row["test_balanced_accuracy"]) for row in split_rows) / len(split_rows)
        min_test_balanced_accuracy = min(_to_float(row["test_balanced_accuracy"]) for row in split_rows)
        summary = {
            "acceptance_posture": "freeze_v117p_cpo_breakout_damage_time_split_external_validation_v1",
            "split_count": len(split_rows),
            "mean_test_balanced_accuracy": round(mean_test_balanced_accuracy, 6),
            "min_test_balanced_accuracy": round(min_test_balanced_accuracy, 6),
            "stability_posture": (
                "candidate_stable_enough_for_further_external_audit"
                if min_test_balanced_accuracy >= 0.5
                else "candidate_unstable_under_time_split"
            ),
            "recommended_next_posture": "audit_breakout_damage_false_positives_with_secondary_reverse_and_heuristic_layers",
        }
        interpretation = [
            "V1.17P does not ask whether the score is strong on the full sample. It asks whether a threshold learned on one time slice survives on another.",
            "The point is not to prove promotion. The point is to stop a neat candidate from surviving only because it was carved inside one tiny window family.",
            "Time-split instability here should block any replay-facing ambition, even if the full-sample gap still looks attractive.",
        ]
        return V117PCpoBreakoutDamageTimeSplitExternalValidationReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117PCpoBreakoutDamageTimeSplitExternalValidationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117PCpoBreakoutDamageTimeSplitExternalValidationAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117o_payload=json.loads((repo_root / "reports" / "analysis" / "v117o_cpo_breakout_damage_external_pool_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117p_cpo_breakout_damage_time_split_external_validation_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
