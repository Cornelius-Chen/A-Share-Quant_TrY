from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130MTransferProgramKLGapClosureTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    authoritative_decision: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "authoritative_decision": self.authoritative_decision,
        }


class V130MTransferProgramKLGapClosureTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.input_path = repo_root / "reports" / "analysis" / "v130l_transfer_program_gap_closure_scenarios_v1.json"

    def analyze(self) -> V130MTransferProgramKLGapClosureTriageReport:
        report = json.loads(self.input_path.read_text(encoding="utf-8"))
        scenario_rows = report["scenario_rows"]
        triage_rows = []
        for row in scenario_rows:
            triage_rows.append(
                {
                    "sector_id": row["sector_id"],
                    "scenario_class": row["scenario_class"],
                    "single_action_reopen_possible": row["single_action_reopen_possible"],
                    "direction": (
                        "monitor_closely_but_do_not_reopen"
                        if row["single_action_reopen_possible"]
                        else "keep_frozen_until_material_local_support_changes"
                    ),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v130m_transfer_program_kl_gap_closure_triage_v1",
            "nearest_candidate_sector_id": scenario_rows[0]["sector_id"] if scenario_rows else None,
            "authoritative_status": "keep_transfer_program_frozen_and_prioritize_gap_closure_monitoring_over_worker_creation",
        }
        authoritative_decision = [
            "Keep the transfer program frozen.",
            "Treat BK0808 as the closest monitored candidate, not as an unlocked worker.",
            "Do not open any new board worker until a candidate closes its same-plane and bridge gaps in the local feed.",
        ]
        return V130MTransferProgramKLGapClosureTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            authoritative_decision=authoritative_decision,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V130MTransferProgramKLGapClosureTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130MTransferProgramKLGapClosureTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130m_transfer_program_kl_gap_closure_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
