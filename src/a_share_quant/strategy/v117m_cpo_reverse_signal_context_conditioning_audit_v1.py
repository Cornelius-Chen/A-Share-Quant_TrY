from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V117MCpoReverseSignalContextConditioningAuditReport:
    summary: dict[str, Any]
    threshold_audit_rows: list[dict[str, Any]]
    top_conditioned_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_audit_rows": self.threshold_audit_rows,
            "top_conditioned_rows": self.top_conditioned_rows,
            "interpretation": self.interpretation,
        }


class V117MCpoReverseSignalContextConditioningAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        rows_path: Path,
        v117k_payload: dict[str, Any],
    ) -> V117MCpoReverseSignalContextConditioningAuditReport:
        base_rows = _load_csv_rows(rows_path)
        score_map = {
            (str(row["signal_trade_date"]), str(row["symbol"]), str(row["action_context"])): _to_float(row["candidate_reverse_score"])
            for row in list(v117k_payload.get("candidate_score_rows", []))
        }
        conditioned_rows = []
        for row in base_rows:
            if str(row.get("board_phase")) not in {"main_markup", "diffusion"}:
                continue
            if str(row.get("action_context")) not in {"add_vs_hold", "reduce_vs_hold", "close_vs_hold"}:
                continue
            key = (str(row["signal_trade_date"]), str(row["symbol"]), str(row["action_context"]))
            enriched = dict(row)
            enriched["candidate_reverse_score"] = score_map.get(key, 0.0)
            conditioned_rows.append(enriched)

        negative_rows = [row for row in conditioned_rows if str(row.get("coarse_label")) == "decrease_expression"]
        non_negative_rows = [row for row in conditioned_rows if str(row.get("coarse_label")) != "decrease_expression"]
        thresholds = sorted({_to_float(row.get("candidate_reverse_score")) for row in conditioned_rows}, reverse=True)

        threshold_audit_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for threshold in thresholds:
            tp = sum(1 for row in negative_rows if _to_float(row.get("candidate_reverse_score")) >= threshold)
            fn = len(negative_rows) - tp
            fp = sum(1 for row in non_negative_rows if _to_float(row.get("candidate_reverse_score")) >= threshold)
            tn = len(non_negative_rows) - fp
            tpr = tp / len(negative_rows) if negative_rows else 0.0
            tnr = tn / len(non_negative_rows) if non_negative_rows else 0.0
            balanced_accuracy = (tpr + tnr) / 2.0
            row = {
                "threshold": round(threshold, 6),
                "tp": tp,
                "fn": fn,
                "fp": fp,
                "tn": tn,
                "negative_recall": round(tpr, 6),
                "non_negative_reject_rate": round(tnr, 6),
                "balanced_accuracy": round(balanced_accuracy, 6),
            }
            threshold_audit_rows.append(row)
            if best_row is None or row["balanced_accuracy"] > best_row["balanced_accuracy"]:
                best_row = row

        conditioned_rows.sort(key=lambda row: _to_float(row.get("candidate_reverse_score")), reverse=True)
        top_conditioned_rows = [
            {
                "signal_trade_date": str(row["signal_trade_date"]),
                "symbol": str(row["symbol"]),
                "board_phase": str(row["board_phase"]),
                "action_context": str(row["action_context"]),
                "coarse_label": str(row["coarse_label"]),
                "candidate_reverse_score": round(_to_float(row["candidate_reverse_score"]), 6),
            }
            for row in conditioned_rows[:20]
        ]

        negative_mean = sum(_to_float(row.get("candidate_reverse_score")) for row in negative_rows) / len(negative_rows) if negative_rows else 0.0
        non_negative_mean = sum(_to_float(row.get("candidate_reverse_score")) for row in non_negative_rows) / len(non_negative_rows) if non_negative_rows else 0.0

        summary = {
            "acceptance_posture": "freeze_v117m_cpo_reverse_signal_context_conditioning_audit_v1",
            "conditioned_row_count": len(conditioned_rows),
            "conditioned_negative_count": len(negative_rows),
            "conditioned_non_negative_count": len(non_negative_rows),
            "negative_mean_score": round(negative_mean, 6),
            "non_negative_mean_score": round(non_negative_mean, 6),
            "mean_score_gap_negative_minus_non_negative": round(negative_mean - non_negative_mean, 6),
            "best_conditioned_threshold": best_row["threshold"] if best_row else 0.0,
            "best_conditioned_balanced_accuracy": best_row["balanced_accuracy"] if best_row else 0.0,
            "conditioning_improves_signal": len(conditioned_rows) < len(base_rows) and negative_mean > non_negative_mean,
            "recommended_next_posture": "if_conditioned_reverse_gap_improves_send_reverse_branch_to_three_run_adversarial_review",
        }
        interpretation = [
            "V1.17M conditions the reverse-signal branch on the actual problem setting: held-position control inside main markup or diffusion, not the entire board history.",
            "This prevents divergence-and-decay rows with trivial zero structure from dominating the score and gives a more honest read on whether the branch can help control drawdown where it actually matters.",
            "The result is still candidate-only. The point is to make the reverse branch comparable to the positive-side branch before the next adversarial review.",
        ]
        return V117MCpoReverseSignalContextConditioningAuditReport(
            summary=summary,
            threshold_audit_rows=threshold_audit_rows,
            top_conditioned_rows=top_conditioned_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117MCpoReverseSignalContextConditioningAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117MCpoReverseSignalContextConditioningAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
        v117k_payload=json.loads((repo_root / "reports" / "analysis" / "v117k_cpo_reverse_signal_candidate_discovery_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117m_cpo_reverse_signal_context_conditioning_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
