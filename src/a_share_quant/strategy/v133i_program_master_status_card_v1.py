from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133IProgramMasterStatusCardReport:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V133IProgramMasterStatusCardAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.cpo_path = repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json"
        self.ca_packaging_path = (
            repo_root / "reports" / "analysis" / "v133b_commercial_aerospace_ab_intraday_packaging_triage_v1.json"
        )
        self.transfer_path = repo_root / "reports" / "analysis" / "v131a_transfer_program_operational_status_card_v1.json"
        self.ca_intraday_path = (
            repo_root / "reports" / "analysis" / "v133g_commercial_aerospace_intraday_heartbeat_status_v1.json"
        )
        self.output_csv = repo_root / "data" / "training" / "program_master_status_card_v1.csv"

    def analyze(self) -> V133IProgramMasterStatusCardReport:
        cpo = json.loads(self.cpo_path.read_text(encoding="utf-8"))
        ca_packaging = json.loads(self.ca_packaging_path.read_text(encoding="utf-8"))
        transfer = json.loads(self.transfer_path.read_text(encoding="utf-8"))
        ca_intraday = json.loads(self.ca_intraday_path.read_text(encoding="utf-8"))

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
                "current_variant": ca_packaging["summary"]["authoritative_status"],
                "next_action": "wait_for_either_transfer_context_or_lawful_intraday_execution_unblock",
            },
            {
                "program_line": "commercial_aerospace_intraday_execution_lane",
                "status": ca_intraday["summary"]["program_status"],
                "current_variant": "intraday_execution_change_gate",
                "next_action": "wait_for_point_in_time_visibility_execution_simulator_and_separate_intraday_replay_lane",
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
            "acceptance_posture": "freeze_v133i_program_master_status_card_v1",
            "line_count": len(status_rows),
            "frozen_line_count": sum(1 for row in status_rows if "frozen" in row["status"]),
            "authoritative_output": "program_master_status_card_ready_for_do_not_drift_posture",
            "status_card_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.33I compresses the whole active research program into a single master status card.",
            "The goal is operational clarity: at this stage, discipline means not drifting into locally frozen lines without an explicit gate opening.",
        ]
        return V133IProgramMasterStatusCardReport(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133IProgramMasterStatusCardReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133IProgramMasterStatusCardAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133i_program_master_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
