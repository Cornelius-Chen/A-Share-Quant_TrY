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
class V119MCpoParticipationTurnoverElgSupportExternalAuditReport:
    summary: dict[str, Any]
    threshold_audit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_audit_rows": self.threshold_audit_rows,
            "interpretation": self.interpretation,
        }


class V119MCpoParticipationTurnoverElgSupportExternalAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v119l_payload: dict[str, Any]) -> V119MCpoParticipationTurnoverElgSupportExternalAuditReport:
        rows = v119l_payload["candidate_score_rows"]
        thresholds = sorted({_to_float(row["participation_turnover_elg_support_score"]) for row in rows}, reverse=True)
        threshold_audit_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for threshold in thresholds:
            tp = sum(bool(row["positive_add_label"]) and _to_float(row["participation_turnover_elg_support_score"]) >= threshold for row in rows)
            fn = sum(bool(row["positive_add_label"]) and _to_float(row["participation_turnover_elg_support_score"]) < threshold for row in rows)
            fp = sum((not bool(row["positive_add_label"])) and _to_float(row["participation_turnover_elg_support_score"]) >= threshold for row in rows)
            tn = sum((not bool(row["positive_add_label"])) and _to_float(row["participation_turnover_elg_support_score"]) < threshold for row in rows)
            positive_recall = tp / (tp + fn) if (tp + fn) else 0.0
            negative_reject_rate = tn / (tn + fp) if (tn + fp) else 0.0
            balanced_accuracy = (positive_recall + negative_reject_rate) / 2.0
            audit_row = {
                "threshold": round(threshold, 6),
                "tp": tp,
                "fn": fn,
                "fp": fp,
                "tn": tn,
                "positive_recall": round(positive_recall, 6),
                "negative_reject_rate": round(negative_reject_rate, 6),
                "balanced_accuracy": round(balanced_accuracy, 6),
            }
            threshold_audit_rows.append(audit_row)
            if best_row is None or audit_row["balanced_accuracy"] > best_row["balanced_accuracy"]:
                best_row = audit_row

        assert best_row is not None
        positive_rows = [row for row in rows if bool(row["positive_add_label"])]
        negative_rows = [row for row in rows if not bool(row["positive_add_label"])]
        positive_mean = sum(_to_float(row["participation_turnover_elg_support_score"]) for row in positive_rows) / len(positive_rows)
        negative_mean = sum(_to_float(row["participation_turnover_elg_support_score"]) for row in negative_rows) / len(negative_rows)
        summary = {
            "acceptance_posture": "freeze_v119m_cpo_participation_turnover_elg_support_external_audit_v1",
            "candidate_discriminator_name": "participation_turnover_elg_support_score_candidate",
            "positive_mean_score": round(positive_mean, 6),
            "negative_mean_score": round(negative_mean, 6),
            "mean_gap_positive_minus_negative": round(positive_mean - negative_mean, 6),
            "best_threshold": best_row["threshold"],
            "best_balanced_accuracy": best_row["balanced_accuracy"],
            "external_pool_signal_clear": best_row["balanced_accuracy"] >= 0.85,
            "recommended_next_posture": "time_split_validate_elg_supported_combo_candidate_if_external_pool_stays_clean",
        }
        interpretation = [
            "V1.19M checks whether the extra-large-flow support term improves broad-pool ordering rather than just patching one holdout bucket.",
            "A true orthogonal support should strengthen or at least preserve the full external surface without blowing up false positives.",
            "If the broad add pool stays clear, the branch deserves chronology budget; otherwise it should be killed quickly.",
        ]
        return V119MCpoParticipationTurnoverElgSupportExternalAuditReport(
            summary=summary,
            threshold_audit_rows=threshold_audit_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V119MCpoParticipationTurnoverElgSupportExternalAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119MCpoParticipationTurnoverElgSupportExternalAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v119l_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v119l_cpo_participation_turnover_elg_support_discovery_v1.json").read_text(
                encoding="utf-8"
            )
        )
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119m_cpo_participation_turnover_elg_support_external_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
