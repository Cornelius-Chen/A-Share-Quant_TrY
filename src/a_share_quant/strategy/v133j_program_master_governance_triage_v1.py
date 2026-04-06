from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133JProgramMasterGovernanceTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V133JProgramMasterGovernanceTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.master_status_path = repo_root / "reports" / "analysis" / "v133i_program_master_status_card_v1.json"

    def analyze(self) -> V133JProgramMasterGovernanceTriageReport:
        master = json.loads(self.master_status_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v133j_program_master_governance_triage_v1",
            "authoritative_status": "freeze_program_lines_and_wait_for_explicit_gate_changes",
            "line_count": master["summary"]["line_count"],
            "frozen_line_count": master["summary"]["frozen_line_count"],
            "authoritative_rule": "when all active lines are frozen behind explicit governance or change gates, the program should not drift into ungated continuation work",
        }
        triage_rows = [
            {
                "component": "program_master_status_card",
                "status": "retain_as_primary_operational_reference",
                "rationale": "all major lines now have explicit frozen states and next actions, so the program should use one control surface instead of ad hoc continuation",
            },
            {
                "component": "ungated_local_continuation",
                "status": "blocked",
                "rationale": "further work on frozen board lines would be drift unless a documented change gate opens",
            },
        ]
        interpretation = [
            "V1.33J freezes the program at the master-governance level.",
            "This is an anti-drift control: future continuation should be triggered by gates, not by the habit of always doing one more local refinement.",
        ]
        return V133JProgramMasterGovernanceTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133JProgramMasterGovernanceTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133JProgramMasterGovernanceTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133j_program_master_governance_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
