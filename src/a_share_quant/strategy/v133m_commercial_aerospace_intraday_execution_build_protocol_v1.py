from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133MCommercialAerospaceIntradayExecutionBuildProtocolReport:
    summary: dict[str, Any]
    prerequisite_rows: list[dict[str, Any]]
    workstream_rows: list[dict[str, Any]]
    sequencing_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "prerequisite_rows": self.prerequisite_rows,
            "workstream_rows": self.workstream_rows,
            "sequencing_rows": self.sequencing_rows,
            "interpretation": self.interpretation,
        }


class V133MCommercialAerospaceIntradayExecutionBuildProtocolAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.governance_package_path = (
            repo_root / "reports" / "analysis" / "v133a_commercial_aerospace_intraday_governance_packaging_v1.json"
        )
        self.unblock_protocol_path = (
            repo_root / "reports" / "analysis" / "v133c_commercial_aerospace_intraday_execution_unblock_protocol_v1.json"
        )
        self.change_gate_path = (
            repo_root / "reports" / "analysis" / "v133f_commercial_aerospace_intraday_reopen_change_gate_v1.json"
        )
        self.master_status_path = repo_root / "reports" / "analysis" / "v133i_program_master_status_card_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_execution_build_protocol_v1.csv"
        )

    def analyze(self) -> V133MCommercialAerospaceIntradayExecutionBuildProtocolReport:
        governance_package = json.loads(self.governance_package_path.read_text(encoding="utf-8"))
        unblock_protocol = json.loads(self.unblock_protocol_path.read_text(encoding="utf-8"))
        change_gate = json.loads(self.change_gate_path.read_text(encoding="utf-8"))
        master_status = json.loads(self.master_status_path.read_text(encoding="utf-8"))

        prerequisite_rows = [
            {
                "prerequisite": "commercial_aerospace_minute_governance_package",
                "status": "ready_frozen_input",
                "source": "v133a_commercial_aerospace_intraday_governance_packaging_v1",
                "detail": governance_package["summary"]["authoritative_output"],
            },
            {
                "prerequisite": "commercial_aerospace_intraday_change_gate",
                "status": "ready_frozen_guardrail",
                "source": "v133f_commercial_aerospace_intraday_reopen_change_gate_v1",
                "detail": change_gate["summary"]["authoritative_rule"],
            },
            {
                "prerequisite": "commercial_aerospace_program_master_freeze",
                "status": "ready_program_context",
                "source": "v133i_program_master_status_card_v1",
                "detail": master_status["summary"]["authoritative_output"],
            },
        ]

        workstream_rows = [
            {
                "build_order": 1,
                "workstream": "point_in_time_intraday_visibility",
                "current_status": "blocked",
                "current_gap": unblock_protocol["requirement_rows"][0]["current_state"],
                "scope": "build a minute-indexed state feed for the first-hour and replay-relevant windows using only same-minute and prior-minute price, volume, and event visibility",
                "inputs": "raw 1min archives, frozen minute supervision registry, day-level event registry converted into minute-visible state updates",
                "deliverables": "point-in-time minute feature table, minute-visible event-state table with first_visible_ts and close-bar activation semantics, explicit timestamp lineage audit",
                "acceptance_gate": "every state column is reconstructible at minute t without using minute t+1 or later, all event/state fields carry first_visible_ts, same-minute aggregates only activate after the bar closes, and seed sessions can be replayed minute by minute",
                "non_goals": "do not change the frozen EOD primary or inject minute rules into current replay",
            },
            {
                "build_order": 2,
                "workstream": "intraday_execution_simulation_surface",
                "current_status": "blocked",
                "current_gap": unblock_protocol["requirement_rows"][1]["current_state"],
                "scope": "build a separate intraday shadow execution simulator that consumes the point-in-time feed and governance ladder actions",
                "inputs": "point-in-time minute feed, action ladder, fee/slippage assumptions, symbol-level minute bars",
                "deliverables": "deterministic fill simulator, explicit trigger-to-fill policy, cost model, no-readd and panic-derisk semantics",
                "acceptance_gate": "trigger, fill, and cost timing are explicit; same-bar future knowledge is impossible; seed sessions can be simulated reproducibly",
                "non_goals": "do not optimize PnL or tune local alpha before the simulator exists",
            },
            {
                "build_order": 3,
                "workstream": "separate_intraday_replay_lane",
                "current_status": "blocked",
                "current_gap": unblock_protocol["requirement_rows"][2]["current_state"],
                "scope": "bind the simulator into a dedicated intraday replay lane that is isolated from the frozen commercial-aerospace EOD primary",
                "inputs": "point-in-time minute feed, intraday execution simulator, frozen EOD primary orders and state as reference only",
                "deliverables": "intraday shadow replay outputs, comparison reports versus frozen EOD baseline, contamination guardrails",
                "acceptance_gate": "intraday experiments run without mutating the EOD baseline, the shadow lane is physically read-only relative to the frozen EOD primary, all outputs are clearly shadow-only, and replay binding is minute-lawful",
                "non_goals": "do not promote intraday execution into the authoritative lane during initial buildout",
            },
        ]

        sequencing_rows = [
            {
                "phase": "phase_1_visibility",
                "depends_on": "frozen minute governance package only",
                "exit_condition": "minute state feed passes timestamp-lineage audit on canonical seed sessions",
            },
            {
                "phase": "phase_2_simulation",
                "depends_on": "phase_1_visibility",
                "exit_condition": "seed sessions simulate deterministically with explicit fill timing and costs",
            },
            {
                "phase": "phase_3_replay_lane",
                "depends_on": "phase_2_simulation",
                "exit_condition": "intraday replay lane exists as a separate shadow surface without contaminating the frozen EOD primary",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(workstream_rows[0].keys()))
            writer.writeheader()
            writer.writerows(workstream_rows)

        summary = {
            "acceptance_posture": "build_v133m_commercial_aerospace_intraday_execution_build_protocol_v1",
            "blocked_requirement_count": unblock_protocol["summary"]["blocked_requirement_count"],
            "ready_prerequisite_count": len(prerequisite_rows),
            "workstream_count": len(workstream_rows),
            "sequencing_phase_count": len(sequencing_rows),
            "protocol_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_execution_build_protocol_ready_for_subagent_audit",
        }
        interpretation = [
            "V1.33M converts the frozen intraday blockers into a concrete three-workstream build protocol.",
            "The protocol is intentionally infrastructural: it defines how to build a lawful intraday lane without reopening board-local alpha drift.",
        ]
        return V133MCommercialAerospaceIntradayExecutionBuildProtocolReport(
            summary=summary,
            prerequisite_rows=prerequisite_rows,
            workstream_rows=workstream_rows,
            sequencing_rows=sequencing_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133MCommercialAerospaceIntradayExecutionBuildProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133MCommercialAerospaceIntradayExecutionBuildProtocolAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133m_commercial_aerospace_intraday_execution_build_protocol_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
