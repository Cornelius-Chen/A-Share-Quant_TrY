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
class V116TCpoQrsThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V116TCpoQrsThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v116q_payload: dict[str, Any],
        v116r_payload: dict[str, Any],
        v116s_payload: dict[str, Any],
    ) -> V116TCpoQrsThreeRunAdversarialTriageReport:
        q_summary = dict(v116q_payload.get("summary", {}))
        r_variant_map = {str(row["variant_name"]): row for row in list(v116r_payload.get("variant_rows", []))}
        s_summary = dict(v116s_payload.get("summary", {}))
        coverage_rows = list(v116s_payload.get("coverage_rows", []))

        corrected_row = dict(r_variant_map.get("corrected_cooled_shadow_candidate", {}))
        hot_row = dict(r_variant_map.get("hot_upper_bound_reference", {}))
        actual_gap_rows = [row for row in coverage_rows if bool(row.get("coverage_gap"))]
        actual_gap_days = [str(row["trade_date"]) for row in actual_gap_rows]
        no_held_days = [
            str(row["trade_date"])
            for row in coverage_rows
            if int(row.get("held_mature_symbol_count", 0)) == 0
        ]

        triage_rows = [
            {
                "triage_target": "expanded_repaired_window_manifest",
                "triage_posture": "retain_as_authoritative_audit_surface",
                "expanded_window_day_count": int(q_summary.get("expanded_repaired_window_day_count", 0)),
                "new_day_count_beyond_top_miss": int(q_summary.get("new_day_count_beyond_top_miss", 0)),
                "reason": "sample_expansion_was_the_right_move_before_any_more_visible_only_replay_facing_steps",
            },
            {
                "triage_target": "corrected_cooled_shadow_candidate",
                "triage_posture": "retain_candidate_only_but_block_more_replay",
                "hit_day_count": int(corrected_row.get("hit_day_count", 0)),
                "new_hit_day_count": int(corrected_row.get("new_hit_day_count", 0)),
                "positive_expectancy_hit_rate": _to_float(corrected_row.get("positive_expectancy_hit_rate")),
                "reason": "expanded_window_validation_failure_on_new_days_is_best_read_as_coverage_failure_not_signal_death",
            },
            {
                "triage_target": "hot_upper_bound_reference",
                "triage_posture": "retain_audit_ceiling_only",
                "hit_day_count": int(hot_row.get("hit_day_count", 0)),
                "new_hit_day_count": int(hot_row.get("new_hit_day_count", 0)),
                "positive_expectancy_hit_rate": _to_float(hot_row.get("positive_expectancy_hit_rate")),
                "reason": "coverage_is_broader_but_line_remains_too_mixed_and_too_hot",
            },
            {
                "triage_target": "expanded_window_candidate_base_table",
                "triage_posture": "coverage_gap_is_current_authoritative_problem",
                "days_with_held_mature_symbols": int(s_summary.get("days_with_held_mature_symbols", 0)),
                "days_with_add_candidate_rows": int(s_summary.get("days_with_add_candidate_rows", 0)),
                "actual_gap_day_count": len(actual_gap_rows),
                "actual_gap_days": actual_gap_days,
                "non_add_eligible_day_count": len(no_held_days),
                "non_add_eligible_days": no_held_days,
                "reason": "new_expanded_days_cannot_be_judged_until_the_intraday_action_timepoint_table_is_rebuilt",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v116t_cpo_qrs_three_run_adversarial_triage_v1",
            "review_scope": "v116q_v116r_v116s",
            "retained_candidate_still_valid": True,
            "replay_facing_expansion_allowed": False,
            "authoritative_current_problem": "expanded_window_candidate_base_coverage_gap",
            "actual_gap_day_count": len(actual_gap_rows),
            "recommended_next_posture": "rebuild_intraday_action_timepoint_table_for_actual_gap_days_before_more_visible_only_validation",
        }
        interpretation = [
            "The V116Q/V116R/V116S triage accepts the wider repaired-window audit surface but refuses to read the zero new-day hits in V116R as a clean signal failure.",
            "The authoritative current diagnosis is that the expanded-window intraday candidate base table never generated add-vs-hold rows for three true held-mature gap days: 2023-11-07, 2024-01-18, and 2024-01-23.",
            "Therefore the next step is table rebuilding, not threshold tuning and not any further replay-facing visible-only expansion.",
        ]
        return V116TCpoQrsThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116TCpoQrsThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116TCpoQrsThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116q_payload=json.loads((repo_root / "reports" / "analysis" / "v116q_cpo_expanded_repaired_window_manifest_v1.json").read_text(encoding="utf-8")),
        v116r_payload=json.loads((repo_root / "reports" / "analysis" / "v116r_cpo_corrected_cooled_shadow_expanded_window_validation_v1.json").read_text(encoding="utf-8")),
        v116s_payload=json.loads((repo_root / "reports" / "analysis" / "v116s_cpo_expanded_window_intraday_candidate_coverage_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116t_cpo_qrs_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
