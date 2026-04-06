from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130YTransferProgramXYChangeGateTriageReport:
    summary: dict[str, Any]
    authoritative_decision: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "authoritative_decision": self.authoritative_decision,
        }


class V130YTransferProgramXYChangeGateTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.input_path = repo_root / "reports" / "analysis" / "v130x_transfer_program_change_detection_protocol_v1.json"

    def analyze(self) -> V130YTransferProgramXYChangeGateTriageReport:
        report = json.loads(self.input_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v130y_transfer_program_xy_change_gate_triage_v1",
            "artifact_count": report["summary"]["artifact_count"],
            "authoritative_status": "static_data_gate_installed_for_transfer_program",
        }
        authoritative_decision = [
            "Keep the transfer program frozen under static data.",
            "Use the monitored artifact list as the authoritative rerun gate.",
            "Reopen transfer analysis only after one or more monitored artifacts change.",
        ]
        return V130YTransferProgramXYChangeGateTriageReport(
            summary=summary,
            authoritative_decision=authoritative_decision,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V130YTransferProgramXYChangeGateTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130YTransferProgramXYChangeGateTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130y_transfer_program_xy_change_gate_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
