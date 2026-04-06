from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134DFCommercialAerospaceIntradayAddPrelaunchHeartbeatV1Report:
    summary: dict[str, Any]
    heartbeat_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "heartbeat_rows": self.heartbeat_rows,
            "interpretation": self.interpretation,
        }


class V134DFCommercialAerospaceIntradayAddPrelaunchHeartbeatV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.prelaunch_status_path = analysis_dir / "v134db_commercial_aerospace_intraday_add_prelaunch_status_card_v1.json"
        self.program_status_path = analysis_dir / "v134dd_program_master_status_card_v3.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_add_prelaunch_heartbeat_v1.csv"
        )

    def analyze(self) -> V134DFCommercialAerospaceIntradayAddPrelaunchHeartbeatV1Report:
        prelaunch_status = json.loads(self.prelaunch_status_path.read_text(encoding="utf-8"))
        program_status = json.loads(self.program_status_path.read_text(encoding="utf-8"))

        next_frontier_row = next(
            row for row in program_status["status_rows"] if row["program_line"] == "commercial_aerospace_next_frontier"
        )

        heartbeat_rows = [
            {"key": "frontier_name", "value": next_frontier_row["current_variant"]},
            {"key": "frontier_state", "value": next_frontier_row["status"]},
            {"key": "opening_posture", "value": next_frontier_row["opening_posture"]},
            {"key": "opening_gate_count", "value": next_frontier_row["opening_gate_count"]},
            {"key": "silent_opening_allowed", "value": next_frontier_row["silent_opening_allowed"]},
            {"key": "ready_to_open_now", "value": False},
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(heartbeat_rows[0].keys()))
            writer.writeheader()
            writer.writerows(heartbeat_rows)

        summary = {
            "acceptance_posture": "freeze_v134df_commercial_aerospace_intraday_add_prelaunch_heartbeat_v1",
            "frontier_name": next_frontier_row["current_variant"],
            "frontier_state": next_frontier_row["status"],
            "opening_gate_count": prelaunch_status["summary"]["opening_gate_count"],
            "silent_opening_allowed": False,
            "ready_to_open_now": False,
            "heartbeat_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_add_prelaunch_heartbeat_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34DF turns the deferred add frontier into a simple heartbeat: named, gated, and explicitly not open now.",
            "The heartbeat exists to prevent repeated continuation messages from being mistaken for permission to start the frontier.",
        ]
        return V134DFCommercialAerospaceIntradayAddPrelaunchHeartbeatV1Report(
            summary=summary,
            heartbeat_rows=heartbeat_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134DFCommercialAerospaceIntradayAddPrelaunchHeartbeatV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134DFCommercialAerospaceIntradayAddPrelaunchHeartbeatV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134df_commercial_aerospace_intraday_add_prelaunch_heartbeat_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
