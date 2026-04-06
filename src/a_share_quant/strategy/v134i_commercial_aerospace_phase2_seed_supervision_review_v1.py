from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134ICommercialAerospacePhase2SeedSupervisionReviewReport:
    summary: dict[str, Any]
    component_rows: list[dict[str, Any]]
    optimization_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "component_rows": self.component_rows,
            "optimization_rows": self.optimization_rows,
            "interpretation": self.interpretation,
        }


class V134ICommercialAerospacePhase2SeedSupervisionReviewAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.attr_path = analysis_dir / "v134e_commercial_aerospace_intraday_seed_simulator_attribution_v1.json"
        self.det_path = analysis_dir / "v134g_commercial_aerospace_intraday_seed_simulator_deterministic_audit_v1.json"
        self.expand_path = analysis_dir / "v132k_commercial_aerospace_local_1min_session_expansion_audit_v1.json"
        self.shadow_path = analysis_dir / "v132o_commercial_aerospace_local_1min_shadow_benefit_audit_v1.json"
        self.transition_path = analysis_dir / "v132u_commercial_aerospace_local_1min_state_transition_audit_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_phase2_seed_supervision_review_v1.csv"
        )

    def analyze(self) -> V134ICommercialAerospacePhase2SeedSupervisionReviewReport:
        attr = json.loads(self.attr_path.read_text(encoding="utf-8"))
        det = json.loads(self.det_path.read_text(encoding="utf-8"))
        expand = json.loads(self.expand_path.read_text(encoding="utf-8"))
        shadow = json.loads(self.shadow_path.read_text(encoding="utf-8"))
        transition = json.loads(self.transition_path.read_text(encoding="utf-8"))

        tier_lookup = {row["trigger_tier"]: row for row in attr["tier_rows"]}
        shadow_tier_lookup = {row["predicted_tier"]: row for row in shadow["tier_rows"]}

        reversal_attr = tier_lookup["reversal_watch"]
        severe_attr = tier_lookup["severe_override_positive"]
        mild_shadow = shadow_tier_lookup["mild_override_watch"]

        component_rows = [
            {
                "component": "seed_determinism",
                "status": "reasonable",
                "detail": (
                    f"double_run_exact_match = {det['summary']['double_run_exact_match']}, "
                    f"monotonic_fill_violation_count = {det['summary']['monotonic_fill_violation_count']}"
                ),
            },
            {
                "component": "seed_clock_honesty",
                "status": "reasonable",
                "detail": (
                    f"duplicate_fill_violation_count = {det['summary']['duplicate_fill_violation_count']}, "
                    f"post_flat_action_violation_count = {det['summary']['post_flat_action_violation_count']}"
                ),
            },
            {
                "component": "reversal_tier_value",
                "status": "strongest_phase2_candidate",
                "detail": (
                    f"same_day_loss_avoided_share = {reversal_attr['same_day_loss_avoided_share']}, "
                    f"order_count = {reversal_attr['order_count']}"
                ),
            },
            {
                "component": "severe_tier_value",
                "status": "retain_as_narrow_emergency_layer",
                "detail": (
                    f"same_day_loss_avoided_share = {severe_attr['same_day_loss_avoided_share']}, "
                    f"broader_hit_count = {expand['summary']['severe_hit_count']}"
                ),
            },
            {
                "component": "mild_tier_execution",
                "status": "not_promotable_for_sell_execution",
                "detail": (
                    f"mean_forward_return_10 = {mild_shadow['mean_forward_return_10']}, "
                    f"negative_forward_notional_share = {mild_shadow['negative_forward_notional_share']}"
                ),
            },
            {
                "component": "broader_hit_surface",
                "status": "sparse_enough_for_guarded_widening_review",
                "detail": (
                    f"expanded_hit_count = {expand['summary']['expanded_hit_count']}, "
                    f"expanded_session_count = {expand['summary']['expanded_session_count']}, "
                    f"max_symbol_hit_rate = {expand['summary']['max_symbol_hit_rate']}"
                ),
            },
            {
                "component": "state_transition_alignment",
                "status": "reasonable",
                "detail": (
                    f"top_transition_pattern = {transition['summary']['top_transition_pattern']}, "
                    f"severe_hits_with_prior_reversal_share = {transition['summary']['severe_hits_with_prior_reversal_share']}"
                ),
            },
        ]

        optimization_rows = [
            {
                "optimization_area": "reversal_first_widening",
                "priority": "high",
                "recommendation": "If phase 2 widens, widen reversal-trigger simulation before any other tier because reversal carries most same-day loss-avoidance in the canonical seed lane.",
            },
            {
                "optimization_area": "mild_as_no_trade_governance",
                "priority": "high",
                "recommendation": "Keep mild as do-not-readd or surveillance only; the mild tier still has positive forward expectancy and should not become an automatic sell trigger.",
            },
            {
                "optimization_area": "severe_as_terminal_guardrail",
                "priority": "medium",
                "recommendation": "Retain severe as the terminal emergency layer, but do not widen it alone without the earlier reversal step because most severe sessions arrive through an ordered escalation path.",
            },
            {
                "optimization_area": "widening_surface_control",
                "priority": "high",
                "recommendation": "If widening begins, use only broader-hit sessions first rather than the full 612-session surface; this preserves sparsity and avoids turning phase 2 into a generic weak-open filter.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(component_rows[0].keys()))
            writer.writeheader()
            writer.writerows(component_rows)

        summary = {
            "acceptance_posture": "freeze_v134i_commercial_aerospace_phase2_seed_supervision_review_v1",
            "seed_session_count": det["summary"]["seed_session_with_orders_count"],
            "same_day_loss_avoided_total": attr["summary"]["same_day_loss_avoided_total"],
            "top_tier_by_same_day_loss_avoided": attr["summary"]["top_tier_by_same_day_loss_avoided"],
            "top_transition_pattern": transition["summary"]["top_transition_pattern"],
            "mild_execution_promotable": False,
            "recommended_widening_surface": "broader_hit_sessions_only",
            "recommended_widening_tiers": ["reversal_watch", "severe_override_positive"],
            "phase2_supervision_verdict": "reasonable_with_targeted_optimization_space",
            "review_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_phase2_seed_supervision_review_ready_for_widening_protocol",
        }
        interpretation = [
            "V1.34I is a supervision review rather than another strategy search. It judges whether the current phase-2 seed training outcomes are internally reasonable and where the next lawful optimization room still exists.",
            "The review concludes that the phase-2 seed simulator is credible as a narrow shadow object, that reversal handling is currently the most useful execution tier, and that mild should remain governance-only.",
        ]
        return V134ICommercialAerospacePhase2SeedSupervisionReviewReport(
            summary=summary,
            component_rows=component_rows,
            optimization_rows=optimization_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ICommercialAerospacePhase2SeedSupervisionReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ICommercialAerospacePhase2SeedSupervisionReviewAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134i_commercial_aerospace_phase2_seed_supervision_review_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
