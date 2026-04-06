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
class V117HCpoBreakoutDamageCandidateAuditReport:
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


class V117HCpoBreakoutDamageCandidateAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v117b_payload: dict[str, Any],
        v117g_payload: dict[str, Any],
    ) -> V117HCpoBreakoutDamageCandidateAuditReport:
        score_rows = list(v117g_payload.get("candidate_score_rows", []))
        q25_rows = [row for row in score_rows if str(row.get("group_name")) == "q25_hit"]
        hot_rows = [row for row in score_rows if str(row.get("group_name")) == "hot_only"]
        thresholds = sorted({_to_float(row.get("candidate_damage_score")) for row in score_rows}, reverse=True)

        threshold_audit_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for threshold in thresholds:
            tp = sum(1 for row in q25_rows if _to_float(row.get("candidate_damage_score")) >= threshold)
            fn = len(q25_rows) - tp
            fp = sum(1 for row in hot_rows if _to_float(row.get("candidate_damage_score")) >= threshold)
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
        rebuilt_day_rows: list[dict[str, Any]] = []
        for signal_trade_date in ("2023-11-07", "2024-01-18", "2024-01-23"):
            day_rows = [row for row in score_rows if str(row.get("signal_trade_date")) == signal_trade_date]
            day_mean = sum(_to_float(row.get("candidate_damage_score")) for row in day_rows) / len(day_rows) if day_rows else 0.0
            rebuilt_day_rows.append(
                {
                    "signal_trade_date": signal_trade_date,
                    "timing_gate": contrast_map[signal_trade_date]["timing_gate"],
                    "final_judgement": contrast_map[signal_trade_date]["final_judgement"],
                    "candidate_damage_score_mean": round(day_mean, 6),
                    "passes_best_threshold": day_mean >= _to_float(best_row["threshold"]) if best_row else False,
                }
            )

        q25_mean = sum(_to_float(row.get("candidate_damage_score")) for row in q25_rows) / len(q25_rows)
        hot_mean = sum(_to_float(row.get("candidate_damage_score")) for row in hot_rows) / len(hot_rows)
        summary = {
            "acceptance_posture": "freeze_v117h_cpo_breakout_damage_candidate_audit_v1",
            "candidate_discriminator_name": str(v117g_payload.get("summary", {}).get("candidate_discriminator_name")),
            "q25_mean_score": round(q25_mean, 6),
            "hot_only_mean_score": round(hot_mean, 6),
            "mean_score_gap_q25_minus_hot_only": round(q25_mean - hot_mean, 6),
            "best_audit_threshold": best_row["threshold"] if best_row else 0.0,
            "best_balanced_accuracy": best_row["balanced_accuracy"] if best_row else 0.0,
            "captures_quality_signal": q25_mean > hot_mean,
            "replaces_timing_gate": False,
            "retained_day_passes_quality_gate": next(row for row in rebuilt_day_rows if row["signal_trade_date"] == "2024-01-18")["passes_best_threshold"],
            "late_good_day_passes_quality_gate": next(row for row in rebuilt_day_rows if row["signal_trade_date"] == "2023-11-07")["passes_best_threshold"],
            "late_weak_day_passes_quality_gate": next(row for row in rebuilt_day_rows if row["signal_trade_date"] == "2024-01-23")["passes_best_threshold"],
            "recommended_next_posture": "if_breakout_damage_score_survives_candidate_audit_run_retained_set_refinement_next_and_keep_candidate_only",
        }
        interpretation = [
            "V1.17H is the first hard audit for the new breakout-damage branch.",
            "It asks the same question as V117D did for the old branch: does the new score separate q=0.25 hits from hot-only rows without pretending to replace timing?",
            "The branch stays candidate-only regardless of outcome. The point is to test whether this is a genuinely different quality-side path worth a second run.",
        ]
        return V117HCpoBreakoutDamageCandidateAuditReport(
            summary=summary,
            threshold_audit_rows=threshold_audit_rows,
            rebuilt_day_rows=rebuilt_day_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117HCpoBreakoutDamageCandidateAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117HCpoBreakoutDamageCandidateAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117b_payload=json.loads((repo_root / "reports" / "analysis" / "v117b_cpo_cooled_q025_quality_contrast_audit_v1.json").read_text(encoding="utf-8")),
        v117g_payload=json.loads((repo_root / "reports" / "analysis" / "v117g_cpo_breakout_damage_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117h_cpo_breakout_damage_candidate_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
