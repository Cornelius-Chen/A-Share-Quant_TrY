from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133LProgramMasterHeartbeatSnapshotReport:
    summary: dict[str, Any]
    heartbeat_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "heartbeat_rows": self.heartbeat_rows,
            "interpretation": self.interpretation,
        }


class V133LProgramMasterHeartbeatSnapshotAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.master_status_path = repo_root / "reports" / "analysis" / "v133i_program_master_status_card_v1.json"
        self.transfer_status_path = repo_root / "reports" / "analysis" / "v131a_transfer_program_operational_status_card_v1.json"
        self.intraday_status_path = (
            repo_root / "reports" / "analysis" / "v133g_commercial_aerospace_intraday_heartbeat_status_v1.json"
        )
        self.output_csv = repo_root / "data" / "training" / "program_master_heartbeat_snapshot_v1.csv"

    def analyze(self) -> V133LProgramMasterHeartbeatSnapshotReport:
        master = json.loads(self.master_status_path.read_text(encoding="utf-8"))
        transfer = json.loads(self.transfer_status_path.read_text(encoding="utf-8"))
        intraday = json.loads(self.intraday_status_path.read_text(encoding="utf-8"))

        heartbeat_rows = [
            {
                "key": "program_status",
                "value": "frozen",
            },
            {
                "key": "frozen_line_count",
                "value": master["summary"]["frozen_line_count"],
            },
            {
                "key": "transfer_nearest_candidate",
                "value": transfer["summary"]["nearest_candidate_sector_id"],
            },
            {
                "key": "transfer_watch_symbol",
                "value": transfer["summary"]["decisive_watch_symbol"],
            },
            {
                "key": "transfer_rerun_required",
                "value": transfer["summary"]["rerun_required"],
            },
            {
                "key": "intraday_rerun_required",
                "value": intraday["summary"]["rerun_required"],
            },
            {
                "key": "intraday_missing_artifact_count",
                "value": intraday["summary"]["missing_artifact_count"],
            },
            {
                "key": "next_program_action",
                "value": "wait_for_explicit_gate_changes_not_local_drift",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(heartbeat_rows[0].keys()))
            writer.writeheader()
            writer.writerows(heartbeat_rows)

        summary = {
            "acceptance_posture": "freeze_v133l_program_master_heartbeat_snapshot_v1",
            "program_status": "frozen",
            "frozen_line_count": master["summary"]["frozen_line_count"],
            "transfer_rerun_required": transfer["summary"]["rerun_required"],
            "intraday_rerun_required": intraday["summary"]["rerun_required"],
            "heartbeat_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "program_master_heartbeat_ready_for_do_not_drift_posture",
        }
        interpretation = [
            "V1.33L compresses the frozen program into a minimal heartbeat snapshot.",
            "The snapshot is meant for fast operational reading: what is frozen, what is closest, and whether any gate has actually opened.",
        ]
        return V133LProgramMasterHeartbeatSnapshotReport(
            summary=summary,
            heartbeat_rows=heartbeat_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133LProgramMasterHeartbeatSnapshotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133LProgramMasterHeartbeatSnapshotAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133l_program_master_heartbeat_snapshot_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
