from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BSCommercialAerospaceSellSideBindingReadinessAuditV1Report:
    summary: dict[str, Any]
    readiness_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "readiness_rows": self.readiness_rows,
            "interpretation": self.interpretation,
        }


class V134BSCommercialAerospaceSellSideBindingReadinessAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.visibility_path = (
            repo_root / "reports" / "analysis" / "v133z_commercial_aerospace_yz_all_session_visibility_triage_v1.json"
        )
        self.seed_sim_path = (
            repo_root / "reports" / "analysis" / "v134g_commercial_aerospace_intraday_seed_simulator_deterministic_audit_v1.json"
        )
        self.phase2_stack_path = (
            repo_root / "reports" / "analysis" / "v134aq_commercial_aerospace_phase2_current_shadow_stack_v4.json"
        )
        self.blocker_path = (
            repo_root / "reports" / "analysis" / "v134bq_commercial_aerospace_reduce_execution_binding_blocker_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_sell_side_binding_readiness_audit_v1.csv"
        )

    def analyze(self) -> V134BSCommercialAerospaceSellSideBindingReadinessAuditV1Report:
        visibility = json.loads(self.visibility_path.read_text(encoding="utf-8"))
        seed_sim = json.loads(self.seed_sim_path.read_text(encoding="utf-8"))
        phase2_stack = json.loads(self.phase2_stack_path.read_text(encoding="utf-8"))
        blocker = json.loads(self.blocker_path.read_text(encoding="utf-8"))

        readiness_rows = [
            {
                "component": "all_session_visibility_surface",
                "status": "ready_as_shadow_input",
                "evidence": f"all_session_count = {visibility['summary']['all_session_count']}",
                "what_it_solves": "minute-lawful state visibility exists across the current six-symbol first-hour surface",
                "remaining_gap": "not yet bound to execution-state transitions",
            },
            {
                "component": "deterministic_seed_simulator",
                "status": "ready_as_shadow_input",
                "evidence": (
                    f"double_run_exact_match = {seed_sim['summary']['double_run_exact_match']}, "
                    f"monotonic_fill_violation_count = {seed_sim['summary']['monotonic_fill_violation_count']}"
                ),
                "what_it_solves": "trigger-to-fill timing and chronology are already deterministic on canonical seeds",
                "remaining_gap": "still session-isolated and not portfolio-state bound",
            },
            {
                "component": "phase2_wider_sell_shadow",
                "status": "ready_as_shadow_reference",
                "evidence": (
                    f"reference = {phase2_stack['summary']['current_phase2_wider_reference']}, "
                    f"same_day_loss_avoided_total = {phase2_stack['summary']['phase2_best_same_day_loss_avoided_total']}"
                ),
                "what_it_solves": "current best sell-side shadow behavior is already frozen on broader-hit surface",
                "remaining_gap": "still same-day shadow and not execution-bound",
            },
            {
                "component": "holdings_aware_sell_binding_surface",
                "status": "missing",
                "evidence": "no portfolio-stateful intraday sell lane exists",
                "what_it_solves": "would connect minute triggers to real held quantity, cooldown state, and do-not-readd state",
                "remaining_gap": "must still be built",
            },
            {
                "component": "isolated_sell_side_shadow_lane",
                "status": "missing",
                "evidence": (
                    f"sell_side_binding_blocker_count = {blocker['summary']['sell_side_binding_blocker_count']}"
                ),
                "what_it_solves": "would bind visibility plus simulator into a read-only sell-side execution lane without touching board reentry yet",
                "remaining_gap": "must still be built",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(readiness_rows[0].keys()))
            writer.writeheader()
            writer.writerows(readiness_rows)

        summary = {
            "acceptance_posture": "freeze_v134bs_commercial_aerospace_sell_side_binding_readiness_audit_v1",
            "ready_shadow_input_count": sum(1 for row in readiness_rows if row["status"] == "ready_as_shadow_input"),
            "ready_shadow_reference_count": sum(
                1 for row in readiness_rows if row["status"] == "ready_as_shadow_reference"
            ),
            "missing_binding_component_count": sum(1 for row in readiness_rows if row["status"] == "missing"),
            "authoritative_output": "commercial_aerospace_sell_side_binding_readiness_ready_for_direction_triage",
            "readiness_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34BS separates what already exists as shadow-grade sell-side infrastructure from what is still missing for binding.",
            "The branch is no longer blocked because it has no sell-side artifacts. It is blocked because those artifacts are not yet connected through a holdings-aware, isolated execution surface.",
        ]
        return V134BSCommercialAerospaceSellSideBindingReadinessAuditV1Report(
            summary=summary,
            readiness_rows=readiness_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BSCommercialAerospaceSellSideBindingReadinessAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BSCommercialAerospaceSellSideBindingReadinessAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bs_commercial_aerospace_sell_side_binding_readiness_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
