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
class V117DCpoContinuationIntegrityCandidateAuditReport:
    summary: dict[str, Any]
    threshold_audit_rows: list[dict[str, Any]]
    rebuilt_day_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_audit_rows": self.threshold_audit_rows,
            "rebuilt_day_rows": self.rebuilt_day_rows,
            "interpretation": self.interpretation,
        }


class V117DCpoContinuationIntegrityCandidateAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v117b_payload: dict[str, Any],
        v117c_payload: dict[str, Any],
    ) -> V117DCpoContinuationIntegrityCandidateAuditReport:
        score_rows = list(v117c_payload.get("candidate_score_rows", []))
        q25_rows = [row for row in score_rows if str(row.get("group_name")) == "q25_hit"]
        hot_rows = [row for row in score_rows if str(row.get("group_name")) == "hot_only"]

        q25_scores = sorted({_to_float(row.get("candidate_quality_score")) for row in q25_rows}, reverse=True)
        hot_scores = sorted({_to_float(row.get("candidate_quality_score")) for row in hot_rows}, reverse=True)
        threshold_candidates = sorted({*_as_list(q25_scores), *_as_list(hot_scores)}, reverse=True)

        threshold_audit_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for threshold in threshold_candidates:
            tp = sum(1 for row in q25_rows if _to_float(row.get("candidate_quality_score")) >= threshold)
            fn = len(q25_rows) - tp
            fp = sum(1 for row in hot_rows if _to_float(row.get("candidate_quality_score")) >= threshold)
            tn = len(hot_rows) - fp
            tpr = tp / len(q25_rows) if q25_rows else 0.0
            tnr = tn / len(hot_rows) if hot_rows else 0.0
            balanced_accuracy = (tpr + tnr) / 2.0
            row = {
                "threshold": round(threshold, 6),
                "tp": tp,
                "fn": fn,
                "fp": fp,
                "tn": tn,
                "q25_recall": round(tpr, 6),
                "hot_reject_rate": round(tnr, 6),
                "balanced_accuracy": round(balanced_accuracy, 6),
            }
            threshold_audit_rows.append(row)
            if best_row is None or row["balanced_accuracy"] > best_row["balanced_accuracy"]:
                best_row = row

        contrast_map = {
            str(row.get("signal_trade_date")): dict(row)
            for row in list(v117b_payload.get("contrast_rows", []))
        }
        rebuilt_day_scores: dict[str, list[float]] = {}
        for row in score_rows:
            date_key = str(row.get("signal_trade_date"))
            if date_key in contrast_map:
                rebuilt_day_scores.setdefault(date_key, []).append(_to_float(row.get("candidate_quality_score")))

        rebuilt_day_rows: list[dict[str, Any]] = []
        for signal_trade_date in ("2023-11-07", "2024-01-18", "2024-01-23"):
            contrast_row = contrast_map[signal_trade_date]
            day_scores = rebuilt_day_scores.get(signal_trade_date, [])
            day_mean_score = sum(day_scores) / len(day_scores) if day_scores else 0.0
            passes_best_threshold = day_mean_score >= _to_float(best_row["threshold"]) if best_row else False
            rebuilt_day_rows.append(
                {
                    "signal_trade_date": signal_trade_date,
                    "timing_gate": str(contrast_row.get("timing_gate")),
                    "final_judgement": str(contrast_row.get("final_judgement")),
                    "avg_expectancy_proxy_3d": _to_float(contrast_row.get("avg_expectancy_proxy_3d")),
                    "avg_max_adverse_return_3d": _to_float(contrast_row.get("avg_max_adverse_return_3d")),
                    "candidate_quality_score_mean": round(day_mean_score, 6),
                    "passes_best_threshold": passes_best_threshold,
                }
            )

        q25_mean = sum(q25_scores) / len(q25_scores) if q25_scores else 0.0
        hot_mean = sum(hot_scores) / len(hot_scores) if hot_scores else 0.0
        late_good_day = next(row for row in rebuilt_day_rows if row["signal_trade_date"] == "2023-11-07")
        retained_day = next(row for row in rebuilt_day_rows if row["signal_trade_date"] == "2024-01-18")
        weak_day = next(row for row in rebuilt_day_rows if row["signal_trade_date"] == "2024-01-23")

        summary = {
            "acceptance_posture": "freeze_v117d_cpo_continuation_integrity_candidate_audit_v1",
            "candidate_discriminator_name": str(v117c_payload.get("summary", {}).get("candidate_discriminator_name")),
            "q25_mean_score": round(q25_mean, 6),
            "hot_only_mean_score": round(hot_mean, 6),
            "mean_score_gap_q25_minus_hot_only": round(q25_mean - hot_mean, 6),
            "best_audit_threshold": best_row["threshold"] if best_row else 0.0,
            "best_balanced_accuracy": best_row["balanced_accuracy"] if best_row else 0.0,
            "captures_quality_signal": q25_mean > hot_mean,
            "replaces_timing_gate": False,
            "late_good_day_still_passes_quality_gate": bool(late_good_day["passes_best_threshold"]),
            "retained_day_passes_quality_gate": bool(retained_day["passes_best_threshold"]),
            "late_weak_day_passes_quality_gate": bool(weak_day["passes_best_threshold"]),
            "standalone_threshold_usable_now": False,
            "recommended_next_posture": "keep_continuation_integrity_as_candidate_quality_component_only_and_do_not_replace_timing_gate_or_retained_visible_only_boundary",
        }

        interpretation = [
            "V1.17D audits whether the continuation-integrity score discovered in V1.17C can stand on its own, instead of assuming any positive mean gap is already a usable discriminator.",
            "The score does carry quality information: retained q=0.25 hits score higher on average than hot-only rows, and the weak late day stays below the best audit threshold.",
            "But the best standalone threshold is too strict to preserve the retained rebuilt day 2024-01-18, while lowering it enough to keep that day would materially increase hot-only leakage. It remains a candidate quality component, not a standalone law.",
        ]
        return V117DCpoContinuationIntegrityCandidateAuditReport(
            summary=summary,
            threshold_audit_rows=threshold_audit_rows,
            rebuilt_day_rows=rebuilt_day_rows,
            interpretation=interpretation,
        )


def _as_list(values: list[float]) -> list[float]:
    return list(values)


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117DCpoContinuationIntegrityCandidateAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117DCpoContinuationIntegrityCandidateAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117b_payload=json.loads((repo_root / "reports" / "analysis" / "v117b_cpo_cooled_q025_quality_contrast_audit_v1.json").read_text(encoding="utf-8")),
        v117c_payload=json.loads((repo_root / "reports" / "analysis" / "v117c_cpo_quality_side_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117d_cpo_continuation_integrity_candidate_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
