from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CTCommercialAerospaceFrontierStatusCardV1Report:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V134CTCommercialAerospaceFrontierStatusCardV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.reduce_handoff_path = analysis_dir / "v134co_commercial_aerospace_cn_reduce_handoff_direction_triage_v1.json"
        self.transition_path = analysis_dir / "v134cq_commercial_aerospace_cp_transition_direction_triage_v1.json"
        self.reduce_heartbeat_path = analysis_dir / "v134cr_commercial_aerospace_reduce_heartbeat_status_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_frontier_status_card_v1.csv"
        )

    def analyze(self) -> V134CTCommercialAerospaceFrontierStatusCardV1Report:
        reduce_handoff = json.loads(self.reduce_handoff_path.read_text(encoding="utf-8"))
        transition = json.loads(self.transition_path.read_text(encoding="utf-8"))
        reduce_heartbeat = json.loads(self.reduce_heartbeat_path.read_text(encoding="utf-8"))

        status_rows = [
            {"key": "active_board", "value": "commercial_aerospace"},
            {"key": "reduce_mainline_status", "value": "frozen"},
            {"key": "reduce_local_residue_policy", "value": "supervision_only"},
            {"key": "reduce_execution_blocker_count", "value": reduce_heartbeat["summary"]["execution_blocker_count"]},
            {"key": "next_frontier", "value": "intraday_add"},
            {"key": "next_frontier_state", "value": "deferred"},
            {"key": "frontier_switch_rule", "value": "explicit_shift_only"},
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "acceptance_posture": "freeze_v134ct_commercial_aerospace_frontier_status_card_v1",
            "reduce_handoff_status": reduce_handoff["summary"]["authoritative_status"],
            "transition_status": transition["summary"]["authoritative_status"],
            "next_frontier": "intraday_add",
            "next_frontier_state": "deferred",
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_frontier_status_card_ready_for_program_refresh",
        }
        interpretation = [
            "V1.34CT compresses commercial-aerospace into a current-frontier status card after reduce handoff completion.",
            "The card says two things at once: reduce is frozen, and intraday add is the next frontier but remains deferred until an explicit shift.",
        ]
        return V134CTCommercialAerospaceFrontierStatusCardV1Report(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CTCommercialAerospaceFrontierStatusCardV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CTCommercialAerospaceFrontierStatusCardV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ct_commercial_aerospace_frontier_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
