from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CVCommercialAerospaceReduceFinalStatusCardV1Report:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V134CVCommercialAerospaceReduceFinalStatusCardV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.handoff_path = analysis_dir / "v134co_commercial_aerospace_cn_reduce_handoff_direction_triage_v1.json"
        self.heartbeat_path = analysis_dir / "v134cr_commercial_aerospace_reduce_heartbeat_status_v1.json"
        self.playbook_path = analysis_dir / "v134cs_commercial_aerospace_reduce_reopen_playbook_v1.json"
        self.frontier_path = analysis_dir / "v134ct_commercial_aerospace_frontier_status_card_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reduce_final_status_card_v1.csv"
        )

    def analyze(self) -> V134CVCommercialAerospaceReduceFinalStatusCardV1Report:
        handoff = json.loads(self.handoff_path.read_text(encoding="utf-8"))
        heartbeat = json.loads(self.heartbeat_path.read_text(encoding="utf-8"))
        playbook = json.loads(self.playbook_path.read_text(encoding="utf-8"))
        frontier = json.loads(self.frontier_path.read_text(encoding="utf-8"))

        status_rows = [
            {"key": "reduce_status", "value": "frozen_mainline"},
            {"key": "reduce_policy", "value": "local_residue_supervision_only"},
            {"key": "execution_binding", "value": "still_blocked"},
            {"key": "execution_blocker_count", "value": heartbeat["summary"]["execution_blocker_count"]},
            {"key": "reopen_policy", "value": "gate_driven_only"},
            {"key": "next_frontier", "value": frontier["summary"]["next_frontier"]},
            {"key": "next_frontier_state", "value": frontier["summary"]["next_frontier_state"]},
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "acceptance_posture": "freeze_v134cv_commercial_aerospace_reduce_final_status_card_v1",
            "reduce_handoff_status": handoff["summary"]["authoritative_status"],
            "reduce_reopen_ready": False,
            "execution_blocker_count": heartbeat["summary"]["execution_blocker_count"],
            "next_frontier": frontier["summary"]["next_frontier"],
            "next_frontier_state": frontier["summary"]["next_frontier_state"],
            "playbook_status": playbook["summary"]["authoritative_output"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_reduce_final_status_card_ready_for_do_not_drift_triage",
        }
        interpretation = [
            "V1.34CV compresses the reduce branch into a final operational status card after handoff completion.",
            "The card is meant to answer the practical question directly: is reduce still an active frontier? The answer is no.",
        ]
        return V134CVCommercialAerospaceReduceFinalStatusCardV1Report(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CVCommercialAerospaceReduceFinalStatusCardV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CVCommercialAerospaceReduceFinalStatusCardV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cv_commercial_aerospace_reduce_final_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
