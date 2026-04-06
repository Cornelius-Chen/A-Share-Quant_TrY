from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134DEProgramMasterGovernanceTriageV3Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134DEProgramMasterGovernanceTriageV3Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.master_status_path = repo_root / "reports" / "analysis" / "v134dd_program_master_status_card_v3.json"

    def analyze(self) -> V134DEProgramMasterGovernanceTriageV3Report:
        master = json.loads(self.master_status_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v134de_program_master_governance_triage_v3",
            "authoritative_status": "freeze_program_lines_with_reduce_complete_and_intraday_add_prelaunch_deferred",
            "line_count": master["summary"]["line_count"],
            "frozen_line_count": master["summary"]["frozen_line_count"],
            "deferred_line_count": master["summary"]["deferred_line_count"],
            "opening_gate_count": master["summary"]["opening_gate_count"],
            "authoritative_rule": "when reduce is frozen complete and the next frontier is deferred with explicit prelaunch gates, the program should hold readiness without frontier drift",
        }
        triage_rows = [
            {
                "component": "reduce_branch",
                "status": "retain_as_frozen_handoff",
                "rationale": "reduce remains complete enough and should only allow local residue maintenance",
            },
            {
                "component": "intraday_add_frontier",
                "status": "retain_as_deferred_prelaunch",
                "rationale": "the next frontier is named, gated, and still blocked from silent opening",
            },
            {
                "component": "ungated_continuation",
                "status": "blocked",
                "rationale": "once the prelaunch gate set exists, continuation without explicit shift becomes pure drift",
            },
        ]
        interpretation = [
            "V1.34DE refreshes the program-level anti-drift judgment after intraday add received a formal prelaunch package.",
            "The program now has a cleaner global sentence: reduce is frozen, add is deferred prelaunch, and nothing in between is justified.",
        ]
        return V134DEProgramMasterGovernanceTriageV3Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V134DEProgramMasterGovernanceTriageV3Report) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134DEProgramMasterGovernanceTriageV3Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134de_program_master_governance_triage_v3",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
