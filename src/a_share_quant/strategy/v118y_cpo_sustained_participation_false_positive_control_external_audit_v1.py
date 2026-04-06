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


@dataclass(slots=True)
class V118YCpoSustainedParticipationFalsePositiveControlExternalAuditReport:
    summary: dict[str, Any]
    threshold_audit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_audit_rows": self.threshold_audit_rows,
            "interpretation": self.interpretation,
        }


class V118YCpoSustainedParticipationFalsePositiveControlExternalAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v118x_payload: dict[str, Any]) -> V118YCpoSustainedParticipationFalsePositiveControlExternalAuditReport:
        rows = list(v118x_payload.get("control_rows", []))
        positives = [row for row in rows if bool(row.get("positive_add_label"))]
        negatives = [row for row in rows if not bool(row.get("positive_add_label"))]
        thresholds = sorted({_to_float(row.get("controlled_score")) for row in rows}, reverse=True)

        threshold_audit_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for threshold in thresholds:
            tp = sum(1 for row in positives if _to_float(row.get("controlled_score")) >= threshold)
            fn = len(positives) - tp
            fp = sum(1 for row in negatives if _to_float(row.get("controlled_score")) >= threshold)
            tn = len(negatives) - fp
            tpr = tp / len(positives) if positives else 0.0
            tnr = tn / len(negatives) if negatives else 0.0
            record = {
                "threshold": round(threshold, 6),
                "tp": tp,
                "fn": fn,
                "fp": fp,
                "tn": tn,
                "positive_recall": round(tpr, 6),
                "negative_reject_rate": round(tnr, 6),
                "balanced_accuracy": round((tpr + tnr) / 2.0, 6),
            }
            threshold_audit_rows.append(record)
            if best_row is None or record["balanced_accuracy"] > best_row["balanced_accuracy"]:
                best_row = record

        positive_mean = sum(_to_float(row.get("controlled_score")) for row in positives) / len(positives)
        negative_mean = sum(_to_float(row.get("controlled_score")) for row in negatives) / len(negatives)
        summary = {
            "acceptance_posture": "freeze_v118y_cpo_sustained_participation_false_positive_control_external_audit_v1",
            "candidate_name": "sustained_participation_non_chase_prior_heat_late_fade_control_candidate",
            "positive_mean_score": round(positive_mean, 6),
            "negative_mean_score": round(negative_mean, 6),
            "controlled_gap_positive_minus_negative": round(positive_mean - negative_mean, 6),
            "best_threshold": best_row["threshold"] if best_row else 0.0,
            "best_balanced_accuracy": best_row["balanced_accuracy"] if best_row else 0.0,
            "recommended_next_posture": "time_split_validate_controlled_score_only_if_materially_better_than_v118u",
        }
        interpretation = [
            "V1.18Y asks one narrow question: does the prior-heat/late-fade control materially improve broader add-pool discrimination for the sustained-participation branch?",
            "If not, this same-family control should be dropped immediately instead of being nursed into another tunnel.",
            "If yes, it still remains candidate-only until the next chronology check.",
        ]
        return V118YCpoSustainedParticipationFalsePositiveControlExternalAuditReport(
            summary=summary,
            threshold_audit_rows=threshold_audit_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118YCpoSustainedParticipationFalsePositiveControlExternalAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V118YCpoSustainedParticipationFalsePositiveControlExternalAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v118x_payload=json.loads((repo_root / "reports" / "analysis" / "v118x_cpo_sustained_participation_false_positive_control_discovery_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118y_cpo_sustained_participation_false_positive_control_external_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
