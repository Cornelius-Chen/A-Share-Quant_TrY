from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CYProgramMasterGovernanceTriageV2Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134CYProgramMasterGovernanceTriageV2Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.master_status_path = repo_root / "reports" / "analysis" / "v134cx_program_master_status_card_v2.json"

    def analyze(self) -> V134CYProgramMasterGovernanceTriageV2Report:
        master = json.loads(self.master_status_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v134cy_program_master_governance_triage_v2",
            "authoritative_status": "freeze_program_lines_with_reduce_complete_and_intraday_add_deferred",
            "line_count": master["summary"]["line_count"],
            "frozen_line_count": master["summary"]["frozen_line_count"],
            "deferred_line_count": master["summary"]["deferred_line_count"],
            "authoritative_rule": "when reduce is frozen complete and the next frontier is explicitly deferred, the program should neither drift inside reduce nor silently open add",
        }
        triage_rows = [
            {
                "component": "reduce_branch",
                "status": "retain_as_frozen_handoff",
                "rationale": "reduce is no longer an active semantic frontier and should only allow local residue maintenance",
            },
            {
                "component": "intraday_add_frontier",
                "status": "named_but_not_opened",
                "rationale": "the next frontier is explicit, but opening it requires a later deliberate shift rather than implied continuation",
            },
            {
                "component": "ungated_continuation",
                "status": "blocked",
                "rationale": "the program now has enough state clarity that habit-based continuation would only create drift",
            },
        ]
        interpretation = [
            "V1.34CY refreshes the program-level anti-drift judgment after reduce handoff completion.",
            "The program now has a sharper state: reduce frozen, add deferred, and no justified ungated continuation in between.",
        ]
        return V134CYProgramMasterGovernanceTriageV2Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CYProgramMasterGovernanceTriageV2Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CYProgramMasterGovernanceTriageV2Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cy_program_master_governance_triage_v2",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
