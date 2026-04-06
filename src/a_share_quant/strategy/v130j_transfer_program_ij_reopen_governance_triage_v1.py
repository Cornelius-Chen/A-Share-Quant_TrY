from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130JTransferProgramIJReopenGovernanceTriageReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V130JTransferProgramIJReopenGovernanceTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.protocol_path = repo_root / "reports" / "analysis" / "v130i_transfer_program_reopen_trigger_protocol_v1.json"

    def analyze(self) -> V130JTransferProgramIJReopenGovernanceTriageReport:
        protocol = json.loads(self.protocol_path.read_text(encoding="utf-8"))
        direction_rows = [
            {
                "direction": "transfer_program_state",
                "status": "freeze_with_watchlist",
                "reason": "The queue should stay frozen, but now under an explicit reopen protocol rather than an open-ended pause.",
            },
            {
                "direction": "new_board_worker",
                "status": "blocked_until_reopen_ready",
                "reason": "No candidate currently clears all three reopen triggers.",
            },
            {
                "direction": "watchlist_monitoring",
                "status": "retain",
                "reason": "The watchlist preserves operational readiness and makes the next reopen auditable instead of discretionary.",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v130j_transfer_program_ij_reopen_governance_triage_v1",
            "reopen_ready_count": protocol["summary"]["reopen_ready_count"],
            "authoritative_status": "freeze_transfer_program_but_keep_explicit_reopen_governance",
            "authoritative_rule": "do_not_restart_board_transfer_without_a_candidate_that_clears_all_reopen_triggers",
        }
        interpretation = [
            "V1.30J turns the transfer freeze into governance rather than drift.",
            "The research program can now stay paused without losing rigor or visibility into what would legitimately reopen it.",
        ]
        return V130JTransferProgramIJReopenGovernanceTriageReport(
            summary=summary,
            direction_rows=direction_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V130JTransferProgramIJReopenGovernanceTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130JTransferProgramIJReopenGovernanceTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130j_transfer_program_ij_reopen_governance_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
