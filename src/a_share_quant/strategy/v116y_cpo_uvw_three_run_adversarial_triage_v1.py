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
class V116YCpoUvwThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    subagent_views: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "subagent_views": self.subagent_views,
            "interpretation": self.interpretation,
        }


class V116YCpoUvwThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v116u_payload: dict[str, Any],
        v116v_payload: dict[str, Any],
        v116w_payload: dict[str, Any],
        v116x_payload: dict[str, Any],
    ) -> V116YCpoUvwThreeRunAdversarialTriageReport:
        u_summary = dict(v116u_payload.get("summary", {}))
        v_summary = dict(v116v_payload.get("summary", {}))
        w_variant_map = {str(row["variant_name"]): row for row in list(v116w_payload.get("variant_rows", []))}
        x_rows = {str(row["signal_trade_date"]): row for row in list(v116x_payload.get("contrast_rows", []))}

        corrected_row = dict(w_variant_map.get("corrected_cooled_shadow_candidate", {}))
        hot_row = dict(w_variant_map.get("hot_upper_bound_reference", {}))

        triage_rows = [
            {
                "triage_target": "expanded_window_candidate_base_rebuild",
                "triage_posture": "retain_as_authoritative_repair",
                "rebuilt_day_count": int(u_summary.get("rebuilt_day_count", 0)),
                "rebuilt_row_count": int(u_summary.get("rebuilt_row_count", 0)),
                "reason": "coverage_repair_is_real_and_should_not_be_reopened",
            },
            {
                "triage_target": "post_rebuild_coverage_status",
                "triage_posture": "freeze_as_clean_precondition",
                "days_with_add_candidate_rows": int(v_summary.get("days_with_add_candidate_rows", 0)),
                "days_with_held_mature_symbols": int(v_summary.get("days_with_held_mature_symbols", 0)),
                "true_coverage_gap_day_count_after_rebuild": int(v_summary.get("true_coverage_gap_day_count_after_rebuild", 0)),
                "reason": "coverage_gap_is_no_longer_the_main_problem",
            },
            {
                "triage_target": "corrected_cooled_shadow_candidate",
                "triage_posture": "retain_candidate_only_but_block_promotion",
                "hit_day_count": int(corrected_row.get("hit_day_count", 0)),
                "new_hit_day_count": int(corrected_row.get("new_hit_day_count", 0)),
                "positive_expectancy_hit_rate": _to_float(corrected_row.get("positive_expectancy_hit_rate")),
                "avg_expectancy_proxy_3d": _to_float(corrected_row.get("avg_expectancy_proxy_3d")),
                "avg_max_adverse_return_3d": _to_float(corrected_row.get("avg_max_adverse_return_3d")),
                "reason": "coverage_repair_partially_rescued_the_line_but_external_extension_remains_narrow",
            },
            {
                "triage_target": "hot_upper_bound_reference",
                "triage_posture": "retain_audit_ceiling_only",
                "hit_day_count": int(hot_row.get("hit_day_count", 0)),
                "new_hit_day_count": int(hot_row.get("new_hit_day_count", 0)),
                "positive_expectancy_hit_rate": _to_float(hot_row.get("positive_expectancy_hit_rate")),
                "reason": "broader_hit_surface_still_comes_with_worse_quality_and_is_not_a_candidate_for_law",
            },
            {
                "triage_target": "rebuilt_new_day_contrast",
                "triage_posture": "quality_not_timing_is_now_the_authoritative_problem",
                "2023_11_07_diagnosis": x_rows["2023-11-07"]["diagnosis"],
                "2024_01_18_diagnosis": x_rows["2024-01-18"]["diagnosis"],
                "2024_01_23_diagnosis": x_rows["2024-01-23"]["diagnosis"],
                "reason": "only_2024_01_18_converts_after_repair_so_the_next_step_should_target_quality_side_discrimination",
            },
        ]

        subagent_views = [
            {
                "reviewer": "Pauli",
                "position": "coverage_fixed_but_rebuilt_rows_vs_old_geometry_remain_a_method_risk",
                "main_judgement": "current_main_problem_is_quality_gate_not_timing",
            },
            {
                "reviewer": "Tesla",
                "position": "2024_01_18_is_the_only_new_day_that_meets_the_narrow_confirmation_style",
                "main_judgement": "keep_working_on_quality_discrimination_not_timing_relitigation",
            },
            {
                "reviewer": "James",
                "position": "coverage_bug_is_gone_and_2024_01_23_non_hit_is_reasonable_due_to_weak_quality",
                "main_judgement": "line_is_near_same_family_boundary_but_not_dead",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v116y_cpo_uvw_three_run_adversarial_triage_v1",
            "review_scope": "v116u_v116v_v116w",
            "coverage_bug_remaining": False,
            "authoritative_current_problem": "quality_discrimination_after_coverage_repair",
            "timing_relitigation_needed_now": False,
            "promotion_allowed": False,
            "recommended_next_posture": "keep_candidate_only_and_test_quality_side_cooled_refinement_without_reopening_timing_or_coverage",
        }
        interpretation = [
            "The U/V/W three-run review accepts the coverage repair as complete and refuses to reopen the old 'missing rows' diagnosis.",
            "The corrected cooled visible-only line was partially rescued by the rebuild, but only one of the three rebuilt new days converts into a corrected cooled hit.",
            "The next problem is therefore quality-side discrimination: 2023-11-07 stays late-only positive, 2024-01-18 converts cleanly, and 2024-01-23 stays late-only and weak.",
        ]
        return V116YCpoUvwThreeRunAdversarialTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            subagent_views=subagent_views,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116YCpoUvwThreeRunAdversarialTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116YCpoUvwThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116u_payload=json.loads((repo_root / "reports" / "analysis" / "v116u_cpo_expanded_window_action_timepoint_rebuild_v1.json").read_text(encoding="utf-8")),
        v116v_payload=json.loads((repo_root / "reports" / "analysis" / "v116v_cpo_expanded_window_candidate_coverage_reaudit_v1.json").read_text(encoding="utf-8")),
        v116w_payload=json.loads((repo_root / "reports" / "analysis" / "v116w_cpo_corrected_cooled_shadow_expanded_window_validation_rebuilt_base_v1.json").read_text(encoding="utf-8")),
        v116x_payload=json.loads((repo_root / "reports" / "analysis" / "v116x_cpo_rebuilt_new_day_timing_quality_contrast_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116y_cpo_uvw_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
