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


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


@dataclass(slots=True)
class V117ECpoContinuationIntegrityRetainedSetRefinementAuditReport:
    summary: dict[str, Any]
    threshold_audit_rows: list[dict[str, Any]]
    retained_score_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_audit_rows": self.threshold_audit_rows,
            "retained_score_rows": self.retained_score_rows,
            "interpretation": self.interpretation,
        }


class V117ECpoContinuationIntegrityRetainedSetRefinementAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v117c_payload: dict[str, Any]) -> V117ECpoContinuationIntegrityRetainedSetRefinementAuditReport:
        retained_rows = [
            dict(row)
            for row in list(v117c_payload.get("candidate_score_rows", []))
            if str(row.get("group_name")) == "q25_hit"
        ]
        positive_rows = [
            row for row in retained_rows
            if _to_float(row.get("expectancy_proxy_3d")) > 0 and _to_float(row.get("max_adverse_return_3d")) > -0.04
        ]
        weak_rows = [row for row in retained_rows if row not in positive_rows]

        thresholds = sorted({_to_float(row.get("candidate_quality_score")) for row in retained_rows}, reverse=True)
        threshold_audit_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for threshold in thresholds:
            tp = sum(1 for row in positive_rows if _to_float(row.get("candidate_quality_score")) >= threshold)
            fn = len(positive_rows) - tp
            fp = sum(1 for row in weak_rows if _to_float(row.get("candidate_quality_score")) >= threshold)
            tn = len(weak_rows) - fp
            tpr = tp / len(positive_rows) if positive_rows else 0.0
            tnr = tn / len(weak_rows) if weak_rows else 0.0
            balanced_accuracy = (tpr + tnr) / 2.0
            row = {
                "threshold": round(threshold, 6),
                "tp": tp,
                "fn": fn,
                "fp": fp,
                "tn": tn,
                "positive_recall": round(tpr, 6),
                "weak_reject_rate": round(tnr, 6),
                "balanced_accuracy": round(balanced_accuracy, 6),
            }
            threshold_audit_rows.append(row)
            if best_row is None or row["balanced_accuracy"] > best_row["balanced_accuracy"]:
                best_row = row

        for row in retained_rows:
            row["positive_under_proxy_definition"] = _to_float(row.get("expectancy_proxy_3d")) > 0 and _to_float(row.get("max_adverse_return_3d")) > -0.04
        retained_rows.sort(key=lambda row: _to_float(row.get("candidate_quality_score")), reverse=True)

        positive_mean = sum(_to_float(row.get("candidate_quality_score")) for row in positive_rows) / len(positive_rows) if positive_rows else 0.0
        weak_mean = sum(_to_float(row.get("candidate_quality_score")) for row in weak_rows) / len(weak_rows) if weak_rows else 0.0

        summary = {
            "acceptance_posture": "freeze_v117e_cpo_continuation_integrity_retained_set_refinement_audit_v1",
            "retained_row_count": len(retained_rows),
            "retained_positive_count": len(positive_rows),
            "retained_weak_count": len(weak_rows),
            "positive_mean_score": round(positive_mean, 6),
            "weak_mean_score": round(weak_mean, 6),
            "mean_score_gap_positive_minus_weak": round(positive_mean - weak_mean, 6),
            "best_retained_threshold": best_row["threshold"] if best_row else 0.0,
            "best_retained_balanced_accuracy": best_row["balanced_accuracy"] if best_row else 0.0,
            "retained_set_refinement_value_clear": positive_mean > weak_mean and _to_float(best_row["balanced_accuracy"]) >= 0.7,
            "recommended_next_posture": "if_retained_refinement_gap_stays_weak_keep_continuation_integrity_as_explanatory_component_not_new_gate",
        }
        interpretation = [
            "V1.17E asks a harder question than V1.17D: not whether the continuation-integrity score separates retained hits from hot-only rows, but whether it adds discrimination inside the retained q=0.25 line itself.",
            "This is the real standalone-law test for the current quality component. If the score cannot separate positive retained rows from weak retained rows, then it is descriptive but not a useful new gate.",
            "The report is therefore still candidate-only and should be read as a refinement audit, not a replay-facing promotion step.",
        ]
        return V117ECpoContinuationIntegrityRetainedSetRefinementAuditReport(
            summary=summary,
            threshold_audit_rows=threshold_audit_rows,
            retained_score_rows=retained_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117ECpoContinuationIntegrityRetainedSetRefinementAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117ECpoContinuationIntegrityRetainedSetRefinementAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117c_payload=json.loads((repo_root / "reports" / "analysis" / "v117c_cpo_quality_side_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117e_cpo_continuation_integrity_retained_set_refinement_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
