from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CXProgramMasterStatusCardV2Report:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V134CXProgramMasterStatusCardV2Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.cpo_path = analysis_dir / "v114t_cpo_replay_integrity_repair_v1.json"
        self.ca_eod_path = analysis_dir / "v126k_commercial_aerospace_authoritative_research_protocol_v1.json"
        self.ca_intraday_governance_path = (
            analysis_dir / "v133a_commercial_aerospace_intraday_governance_packaging_v1.json"
        )
        self.reduce_final_path = analysis_dir / "v134cv_commercial_aerospace_reduce_final_status_card_v1.json"
        self.frontier_path = analysis_dir / "v134ct_commercial_aerospace_frontier_status_card_v1.json"
        self.transfer_path = analysis_dir / "v131a_transfer_program_operational_status_card_v1.json"
        self.output_csv = repo_root / "data" / "training" / "program_master_status_card_v2.csv"

    def analyze(self) -> V134CXProgramMasterStatusCardV2Report:
        cpo = json.loads(self.cpo_path.read_text(encoding="utf-8"))
        ca_eod = json.loads(self.ca_eod_path.read_text(encoding="utf-8"))
        ca_intraday_governance = json.loads(self.ca_intraday_governance_path.read_text(encoding="utf-8"))
        reduce_final = json.loads(self.reduce_final_path.read_text(encoding="utf-8"))
        frontier = json.loads(self.frontier_path.read_text(encoding="utf-8"))
        transfer = json.loads(self.transfer_path.read_text(encoding="utf-8"))

        status_rows = [
            {
                "program_line": "cpo_lawful_eod_primary",
                "status": "frozen_authoritative",
                "current_variant": "v114t_cpo_replay_integrity_repair_v1",
                "next_action": cpo["summary"]["recommended_next_posture"],
            },
            {
                "program_line": "commercial_aerospace_lawful_eod_primary",
                "status": "frozen_authoritative",
                "current_variant": "tail_weakdrift_full",
                "next_action": "retain_frozen_primary_and_do_not_resume_board_local_replay_tuning",
            },
            {
                "program_line": "commercial_aerospace_intraday_governance_package",
                "status": "frozen_packaged",
                "current_variant": ca_intraday_governance["summary"]["authoritative_output"],
                "next_action": "retain minute governance package as supervision-only reference",
            },
            {
                "program_line": "commercial_aerospace_reduce_branch",
                "status": "frozen_mainline",
                "current_variant": reduce_final["summary"]["authoritative_output"],
                "next_action": "allow only local residue supervision and do not drift",
            },
            {
                "program_line": "commercial_aerospace_next_frontier",
                "status": frontier["summary"]["next_frontier_state"],
                "current_variant": frontier["summary"]["next_frontier"],
                "next_action": "wait for later explicit shift before opening intraday add",
            },
            {
                "program_line": "transfer_program",
                "status": transfer["summary"]["program_status"],
                "current_variant": transfer["summary"]["nearest_candidate_sector_id"],
                "next_action": transfer["status_rows"][-1]["status_value"],
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "acceptance_posture": "freeze_v134cx_program_master_status_card_v2",
            "line_count": len(status_rows),
            "frozen_line_count": sum(1 for row in status_rows if "frozen" in row["status"]),
            "deferred_line_count": sum(1 for row in status_rows if row["status"] == "deferred"),
            "authoritative_output": "program_master_status_card_v2_ready_for_updated_do_not_drift_posture",
            "status_card_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CX refreshes the program master card after reduce was frozen into a handoff package.",
            "The operational point is that the program now has a named next frontier without silently opening it.",
        ]
        return V134CXProgramMasterStatusCardV2Report(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CXProgramMasterStatusCardV2Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CXProgramMasterStatusCardV2Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cx_program_master_status_card_v2",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
