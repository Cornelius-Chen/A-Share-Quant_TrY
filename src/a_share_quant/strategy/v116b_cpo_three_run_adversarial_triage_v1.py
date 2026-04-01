from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V116BCpoThreeRunAdversarialTriageReport:
    summary: dict[str, Any]
    findings: list[dict[str, Any]]
    retained_conclusions: list[dict[str, Any]]
    do_not_promote: list[dict[str, Any]]
    hard_constraints: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "findings": self.findings,
            "retained_conclusions": self.retained_conclusions,
            "do_not_promote": self.do_not_promote,
            "hard_constraints": self.hard_constraints,
            "interpretation": self.interpretation,
        }


class V116BCpoThreeRunAdversarialTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V116BCpoThreeRunAdversarialTriageReport:
        v115p = json.loads((self.repo_root / "reports" / "analysis" / "v115p_cpo_intraday_timing_aware_overlay_replay_v1.json").read_text(encoding="utf-8"))
        v115q = json.loads((self.repo_root / "reports" / "analysis" / "v115q_cpo_broader_strict_add_timing_audit_v1.json").read_text(encoding="utf-8"))
        v115r = json.loads((self.repo_root / "reports" / "analysis" / "v115r_cpo_broader_timing_aware_overlay_filter_comparison_v1.json").read_text(encoding="utf-8"))

        findings = [
            {
                "severity": "high",
                "axis": "methodology_and_overfit",
                "finding": "The broader timing-aware line is still being judged on a very small reused sample. V115Q widens to only 9 strict add contexts, while V115P still relies on 4 overlay orders.",
                "evidence": {
                    "V115Q.strict_add_context_row_count": v115q["summary"]["strict_add_context_row_count"],
                    "V115P.strict_overlay_order_count": v115p["summary"]["strict_overlay_order_count"],
                },
            },
            {
                "severity": "high",
                "axis": "execution_and_timing_realism",
                "finding": "Timing-aware execution is directionally correct, but checkpoint and fill timing remain optimistic enough to require candidate-only treatment.",
                "evidence": {
                    "V115Q.intraday_same_session_count": v115q["summary"]["intraday_same_session_count"],
                    "V115P.timing_bucket_used": v115p["summary"]["timing_bucket_used"],
                    "V115P.final_equity_delta_vs_baseline": v115p["summary"]["final_equity_delta_vs_baseline"],
                },
            },
            {
                "severity": "high",
                "axis": "training_and_label_quality",
                "finding": "Future-looking labels are still bleeding into filter definitions. In V115R, positive_expectancy_only and action_favored_only are useful for audit, but not legal execution filters.",
                "evidence": {
                    "V115Q.positive_expectancy_count": v115q["summary"]["positive_expectancy_count"],
                    "V115Q.action_favored_count": v115q["summary"]["action_favored_count"],
                    "V115R.best_variant_by_equity": v115r["summary"]["best_variant_by_equity"],
                },
            },
        ]

        retained_conclusions = [
            {
                "statement": "Strict intraday add-band signals are genuinely intraday-visible in the current CPO sample and should not be forced into a uniform T+1-open bucket.",
                "evidence": {
                    "V115Q.intraday_same_session_count": v115q["summary"]["intraday_same_session_count"],
                    "V115Q.post_close_or_next_day_count": v115q["summary"]["post_close_or_next_day_count"],
                },
            },
            {
                "statement": "Timing-aware execution has real candidate value on top of the repaired replay.",
                "evidence": {
                    "V115P.baseline_final_equity": v115p["summary"]["baseline_final_equity"],
                    "V115P.timing_aware_overlay_final_equity": v115p["summary"]["timing_aware_overlay_final_equity"],
                    "V115P.timing_aware_overlay_max_drawdown": v115p["summary"]["timing_aware_overlay_max_drawdown"],
                },
            },
            {
                "statement": "Broader timing-aware overlay variants should be retained in parallel rather than collapsed into a single promoted law.",
                "evidence": {
                    "V115R.variant_count": v115r["summary"]["variant_count"],
                    "V115R.cleanest_variant_by_drawdown": v115r["summary"]["cleanest_variant_by_drawdown"],
                },
            },
        ]

        do_not_promote = [
            {
                "target": "V115R:all_strict_add_context",
                "reason": "Highest equity but too permissive; it admits negative-expectancy strict hits and remains highly sample-bound.",
                "evidence": next(row for row in v115r["variant_rows"] if row["variant_name"] == "all_strict_add_context"),
            },
            {
                "target": "V115R:positive_expectancy_only",
                "reason": "Cleaner than the raw broader variant, but it still uses future outcome labels in the filter definition and therefore cannot be promoted as executable law.",
                "evidence": next(row for row in v115r["variant_rows"] if row["variant_name"] == "positive_expectancy_only"),
            },
            {
                "target": "V115R:action_favored_only / positive_and_favored",
                "reason": "Both rely on post-hoc labels and remain audit-only filters.",
                "evidence": [
                    next(row for row in v115r["variant_rows"] if row["variant_name"] == "action_favored_only"),
                    next(row for row in v115r["variant_rows"] if row["variant_name"] == "positive_and_favored"),
                ],
            },
        ]

        hard_constraints = [
            {
                "constraint_id": "no_future_label_in_filter_definition",
                "priority": 1,
                "statement": "Any intraday overlay filter may use only point-in-time-visible fields. expectancy_proxy_3d and action_favored_3d are audit-only labels and are forbidden inside executable filter definitions.",
            },
            {
                "constraint_id": "keep_intraday_line_held_position_only",
                "priority": 2,
                "statement": "Until broader revalidation succeeds, timing-aware intraday overlays remain held-position only and cannot open fresh admissions.",
            },
            {
                "constraint_id": "retain_parallel_candidate_postures",
                "priority": 3,
                "statement": "Carry broader timing-aware variants in parallel and compare them under future repaired-window validation rather than collapsing them into one promoted law.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v116b_cpo_three_run_adversarial_triage_v1",
            "triage_window": ["V115P", "V115Q", "V115R"],
            "reviewer_count": 3,
            "retained_conclusion_count": len(retained_conclusions),
            "do_not_promote_count": len(do_not_promote),
            "hard_constraint_count": len(hard_constraints),
            "recommended_next_posture": "continue_candidate_revalidation_under_no_future_label_filter_constraint",
        }
        interpretation = [
            "V1.16B turns the first three-run adversarial review into a formal triage object rather than leaving the critique in chat only.",
            "The triage does not reverse the timing-aware direction, but it sharply narrows what may be treated as executable versus what must stay audit-only.",
            "The single most important brake is now explicit: future-looking action labels may grade intraday filters after the fact, but may not define them.",
        ]
        return V116BCpoThreeRunAdversarialTriageReport(
            summary=summary,
            findings=findings,
            retained_conclusions=retained_conclusions,
            do_not_promote=do_not_promote,
            hard_constraints=hard_constraints,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V116BCpoThreeRunAdversarialTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116BCpoThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116b_cpo_three_run_adversarial_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
