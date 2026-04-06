from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133KProgramReopenPlaybookReport:
    summary: dict[str, Any]
    playbook_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "playbook_rows": self.playbook_rows,
            "interpretation": self.interpretation,
        }


class V133KProgramReopenPlaybookAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.master_status_path = repo_root / "reports" / "analysis" / "v133i_program_master_status_card_v1.json"
        self.transfer_rerun_path = (
            repo_root / "reports" / "analysis" / "v131c_transfer_program_rerun_command_sheet_v1.json"
        )
        self.transfer_gate_path = (
            repo_root / "reports" / "analysis" / "v130x_transfer_program_change_detection_protocol_v1.json"
        )
        self.intraday_gate_path = (
            repo_root / "reports" / "analysis" / "v133f_commercial_aerospace_intraday_reopen_change_gate_v1.json"
        )
        self.output_csv = repo_root / "data" / "training" / "program_reopen_playbook_v1.csv"

    def analyze(self) -> V133KProgramReopenPlaybookReport:
        master = json.loads(self.master_status_path.read_text(encoding="utf-8"))
        transfer_rerun = json.loads(self.transfer_rerun_path.read_text(encoding="utf-8"))
        transfer_gate = json.loads(self.transfer_gate_path.read_text(encoding="utf-8"))
        intraday_gate = json.loads(self.intraday_gate_path.read_text(encoding="utf-8"))

        playbook_rows = [
            {
                "program_line": "cpo_lawful_eod_primary",
                "current_status": "frozen_authoritative",
                "gate_type": "manual_research_review",
                "reopen_trigger": "explicit decision to rerun under-exposure or sizing review on the frozen lawful replay",
                "command_hint": "use the existing CPO replay/sizing review chain; do not invent a new board-local discovery branch first",
            },
            {
                "program_line": "commercial_aerospace_lawful_eod_primary",
                "current_status": "frozen_authoritative",
                "gate_type": "manual_research_review",
                "reopen_trigger": "only if a genuinely new lawful board-local context appears; do not reopen for minor replay tuning",
                "command_hint": "start from the frozen primary and governance stack, not from a new local replay search",
            },
            {
                "program_line": "commercial_aerospace_intraday_execution_lane",
                "current_status": "frozen",
                "gate_type": "infrastructure_change_gate",
                "reopen_trigger": "all blocked intraday execution requirements are satisfied",
                "command_hint": "rebuild from the frozen minute governance package after point-in-time visibility, execution simulator, and separate intraday replay lane exist",
            },
            {
                "program_line": "transfer_program",
                "current_status": "frozen",
                "gate_type": "file_change_gate",
                "reopen_trigger": "one of the watched sector/symbol support artifacts changes and the same-plane gate opens",
                "command_hint": transfer_rerun["summary"].get("authoritative_rule", "use v131c rerun chain once the transfer change gate opens"),
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(playbook_rows[0].keys()))
            writer.writeheader()
            writer.writerows(playbook_rows)

        summary = {
            "acceptance_posture": "freeze_v133k_program_reopen_playbook_v1",
            "line_count": len(playbook_rows),
            "transfer_watched_artifact_count": transfer_gate["summary"]["artifact_count"],
            "intraday_missing_artifact_count": intraday_gate["summary"]["missing_artifact_count"],
            "playbook_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "program_reopen_playbook_ready_for_gate_driven_restart",
        }
        interpretation = [
            "V1.33K converts the frozen program state into a practical reopen playbook.",
            "The playbook is not a new research line; it is the operational handoff for future gate-driven restarts.",
        ]
        return V133KProgramReopenPlaybookReport(
            summary=summary,
            playbook_rows=playbook_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133KProgramReopenPlaybookReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133KProgramReopenPlaybookAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133k_program_reopen_playbook_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
