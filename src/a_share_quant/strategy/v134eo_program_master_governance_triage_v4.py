from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134EOProgramMasterGovernanceTriageV4Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134EOProgramMasterGovernanceTriageV4Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.master_status_path = repo_root / "reports" / "analysis" / "v134en_program_master_status_card_v4.json"

    def analyze(self) -> V134EOProgramMasterGovernanceTriageV4Report:
        master = json.loads(self.master_status_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "open_v134eo_program_master_governance_triage_v4",
            "authoritative_status": "open_program_frontier_with_intraday_add_supervision_only_and_reduce_frozen",
            "line_count": master["summary"]["line_count"],
            "frozen_line_count": master["summary"]["frozen_line_count"],
            "opened_supervision_line_count": master["summary"]["opened_supervision_line_count"],
            "authoritative_rule": "the program may now progress inside intraday add, but only at supervision scope while reduce stays frozen",
        }
        triage_rows = [
            {
                "component": "reduce_branch",
                "status": "keep_frozen",
                "rationale": "reduce remains complete enough and should not reopen while add is starting",
            },
            {
                "component": "intraday_add_frontier",
                "status": "opened_supervision_only",
                "rationale": "the next frontier is now active, but only in registry / visibility / labeling layers",
            },
            {
                "component": "execution_authority",
                "status": "blocked",
                "rationale": "opening supervision does not grant execution or replay-facing authority",
            },
        ]
        interpretation = [
            "V1.34EO refreshes the program-level governance judgment after the add frontier shift.",
            "The new global sentence is simple: reduce stays frozen, add is open, but only as supervision.",
        ]
        return V134EOProgramMasterGovernanceTriageV4Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V134EOProgramMasterGovernanceTriageV4Report) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EOProgramMasterGovernanceTriageV4Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134eo_program_master_governance_triage_v4",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
