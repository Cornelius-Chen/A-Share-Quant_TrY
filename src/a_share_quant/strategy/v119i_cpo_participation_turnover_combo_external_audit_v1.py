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
class V119ICpoParticipationTurnoverComboExternalAuditReport:
    summary: dict[str, Any]
    threshold_audit_rows: list[dict[str, Any]]
    scored_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_audit_rows": self.threshold_audit_rows,
            "scored_rows": self.scored_rows,
            "interpretation": self.interpretation,
        }


class V119ICpoParticipationTurnoverComboExternalAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v119h_payload: dict[str, Any]) -> V119ICpoParticipationTurnoverComboExternalAuditReport:
        rows = list(v119h_payload.get("candidate_score_rows", []))
        positive_rows = [row for row in rows if bool(row.get("positive_add_label"))]
        negative_rows = [row for row in rows if not bool(row.get("positive_add_label"))]
        thresholds = sorted({_to_float(row.get("participation_turnover_combo_score")) for row in rows}, reverse=True)

        threshold_audit_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for threshold in thresholds:
            tp = sum(1 for row in positive_rows if _to_float(row.get("participation_turnover_combo_score")) >= threshold)
            fn = len(positive_rows) - tp
            fp = sum(1 for row in negative_rows if _to_float(row.get("participation_turnover_combo_score")) >= threshold)
            tn = len(negative_rows) - fp
            tpr = tp / len(positive_rows) if positive_rows else 0.0
            tnr = tn / len(negative_rows) if negative_rows else 0.0
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

        positive_mean = sum(_to_float(row.get("participation_turnover_combo_score")) for row in positive_rows) / len(positive_rows)
        negative_mean = sum(_to_float(row.get("participation_turnover_combo_score")) for row in negative_rows) / len(negative_rows)

        summary = {
            "acceptance_posture": "freeze_v119i_cpo_participation_turnover_combo_external_audit_v1",
            "candidate_discriminator_name": "participation_turnover_combo_score_candidate",
            "positive_mean_score": round(positive_mean, 6),
            "negative_mean_score": round(negative_mean, 6),
            "mean_gap_positive_minus_negative": round(positive_mean - negative_mean, 6),
            "best_threshold": best_row["threshold"] if best_row else 0.0,
            "best_balanced_accuracy": best_row["balanced_accuracy"] if best_row else 0.0,
            "external_pool_signal_clear": positive_mean > negative_mean,
            "recommended_next_posture": "time_split_validate_combo_candidate_if_external_pool_gap_remains_positive",
        }
        interpretation = [
            "V1.19I asks whether combining the strongest live intraday line and the new Tushare turnover-discipline line creates a genuinely cleaner broad-pool ordering.",
            "The branch only deserves chronology budget if the combined signal outperforms either side alone on the add pool.",
            "If the gain is fake, the project should revert to the separate branches rather than keep stacking.",
        ]
        return V119ICpoParticipationTurnoverComboExternalAuditReport(
            summary=summary,
            threshold_audit_rows=threshold_audit_rows,
            scored_rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V119ICpoParticipationTurnoverComboExternalAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119ICpoParticipationTurnoverComboExternalAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v119h_payload=json.loads((repo_root / "reports" / "analysis" / "v119h_cpo_participation_turnover_combo_discovery_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119i_cpo_participation_turnover_combo_external_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
