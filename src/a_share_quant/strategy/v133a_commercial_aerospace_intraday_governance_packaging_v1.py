from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133ACommercialAerospaceIntradayGovernancePackagingReport:
    summary: dict[str, Any]
    transferable_rows: list[dict[str, Any]]
    non_transferable_rows: list[dict[str, Any]]
    execution_blocker_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "transferable_rows": self.transferable_rows,
            "non_transferable_rows": self.non_transferable_rows,
            "execution_blocker_rows": self.execution_blocker_rows,
            "interpretation": self.interpretation,
        }


class V133ACommercialAerospaceIntradayGovernancePackagingAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.stack_v3_path = (
            repo_root / "reports" / "analysis" / "v132w_commercial_aerospace_governance_stack_refresh_v3.json"
        )
        self.case_panel_path = (
            repo_root / "reports" / "analysis" / "v132z_commercial_aerospace_yz_intraday_case_panel_triage_v1.json"
        )
        self.state_transition_path = (
            repo_root / "reports" / "analysis" / "v132v_commercial_aerospace_uv_local_1min_state_transition_triage_v1.json"
        )
        self.shadow_benefit_path = (
            repo_root / "reports" / "analysis" / "v132p_commercial_aerospace_op_local_1min_shadow_benefit_triage_v1.json"
        )

    def analyze(self) -> V133ACommercialAerospaceIntradayGovernancePackagingReport:
        stack_v3 = json.loads(self.stack_v3_path.read_text(encoding="utf-8"))
        case_panel = json.loads(self.case_panel_path.read_text(encoding="utf-8"))
        state_transition = json.loads(self.state_transition_path.read_text(encoding="utf-8"))
        shadow_benefit = json.loads(self.shadow_benefit_path.read_text(encoding="utf-8"))

        transferable_rows = [
            {
                "component": "tiered_seed_registry",
                "status": "transferable_method",
                "rule": "start minute work from explicit severe / reversal / mild supervision seeds rather than undifferentiated intraday failures",
            },
            {
                "component": "bounded_false_positive_audit",
                "status": "transferable_method",
                "rule": "pressure-test minute rules first on replay buy executions, then on broader local sessions, before any replay-side discussion",
            },
            {
                "component": "shadow_benefit_audit",
                "status": "transferable_method",
                "rule": "upgrade minute governance only when a narrow flagged slice captures disproportionate later downside notional",
            },
            {
                "component": "action_ladder_translation",
                "status": "transferable_method",
                "rule": "translate minute tiers into governance actions such as emergency-exit, panic-derisk, and do-not-readd before building intraday execution logic",
            },
            {
                "component": "state_transition_audit",
                "status": "transferable_method",
                "rule": "check whether broader hit sessions evolve through ordered escalation rather than relying on terminal labels alone",
            },
            {
                "component": "visual_case_panel",
                "status": "transferable_method",
                "rule": "freeze a canonical seed-session panel so future intraday work stays anchored to inspectable examples",
            },
        ]

        non_transferable_rows = [
            {
                "component": "commercial_aerospace_symbol_set",
                "status": "local_only",
                "rule": "the 6 seed sessions and their symbols remain commercial-aerospace-specific and must not be copied as another board's supervision source",
            },
            {
                "component": "commercial_aerospace_threshold_geometry",
                "status": "local_only",
                "rule": "the exact return, drawdown, and close-location thresholds were fit to the local commercial-aerospace minute branch and need local revalidation elsewhere",
            },
            {
                "component": "commercial_aerospace_phase_context",
                "status": "local_only",
                "rule": "preheat / impulse semantics and their chronology belong to this theme and cannot be assumed on another archetype",
            },
        ]

        execution_blocker_rows = [
            {
                "blocker": "point_in_time_intraday_visibility",
                "status": "unresolved",
                "detail": "the minute branch still lacks a lawful intraday execution path with point-in-time visible event and state updates",
            },
            {
                "blocker": "execution_simulation_surface",
                "status": "unresolved",
                "detail": "there is no lawful intraday fill/execution model attached to the minute governance stack yet",
            },
            {
                "blocker": "replay_binding",
                "status": "unresolved",
                "detail": "the frozen EOD replay remains authoritative and the minute branch is still governance-only, not replay-facing",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v133a_commercial_aerospace_intraday_governance_packaging_v1",
            "current_primary_variant": stack_v3["summary"]["current_primary_variant"],
            "governance_layer_count": stack_v3["summary"]["governance_layer_count"],
            "shadow_benefit_status": shadow_benefit["summary"]["authoritative_status"],
            "state_transition_status": state_transition["summary"]["authoritative_status"],
            "case_panel_status": case_panel["summary"]["authoritative_status"],
            "authoritative_output": "commercial_aerospace_intraday_governance_package_frozen_for_transfer_or_future_lawful_intraday_design",
        }
        interpretation = [
            "V1.33A packages the completed commercial-aerospace minute-governance branch into transferable method pieces, local-only pieces, and explicit execution blockers.",
            "The output is not a replay promotion; it is a portability and readiness document for the next stage.",
        ]
        return V133ACommercialAerospaceIntradayGovernancePackagingReport(
            summary=summary,
            transferable_rows=transferable_rows,
            non_transferable_rows=non_transferable_rows,
            execution_blocker_rows=execution_blocker_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133ACommercialAerospaceIntradayGovernancePackagingReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133ACommercialAerospaceIntradayGovernancePackagingAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133a_commercial_aerospace_intraday_governance_packaging_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
