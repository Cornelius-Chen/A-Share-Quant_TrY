from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129RBK0480AerospaceAviationTransferWorkerKickoffTriageReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V129RBK0480AerospaceAviationTransferWorkerKickoffTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.transfer_triage_path = repo_root / "reports" / "analysis" / "v129p_commercial_aerospace_nop_transfer_preparation_triage_v1.json"
        self.world_model_path = repo_root / "reports" / "analysis" / "v129q_bk0480_aerospace_aviation_board_world_model_v1.json"

    def analyze(self) -> V129RBK0480AerospaceAviationTransferWorkerKickoffTriageReport:
        transfer_triage = json.loads(self.transfer_triage_path.read_text(encoding="utf-8"))
        world_model = json.loads(self.world_model_path.read_text(encoding="utf-8"))

        direction_rows = [
            {
                "direction": "bk0480_board_worker",
                "status": "start",
                "reason": "Transfer target and portability boundaries are now frozen, and BK0480 has enough local snapshot support to open role grammar.",
            },
            {
                "direction": "commercial_aerospace_local_windows",
                "status": "blocked",
                "reason": "BK0480 worker must relearn local chronology instead of importing commercial-aerospace main/post windows.",
            },
            {
                "direction": "commercial_aerospace_symbol_pressure_map",
                "status": "blocked",
                "reason": "BK0480 worker must not reuse symbol facts from commercial aerospace.",
            },
            {
                "direction": "next_phase",
                "status": "role_grammar",
                "reason": world_model["summary"]["recommended_next_posture"],
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v129r_bk0480_aerospace_aviation_transfer_worker_kickoff_triage_v1",
            "authoritative_status": "bk0480_transfer_worker_started_from_dual_core_world_model_with_local_reset",
            "selected_board": transfer_triage["summary"]["recommended_next_primary_board"],
            "selected_board_name": world_model["summary"]["board_name"],
            "next_phase": world_model["summary"]["next_phase"],
            "authoritative_rule": "start_bk0480_from_transfer_packaging_but_force_local_role_and_time relearning before any control extraction or replay",
        }
        interpretation = [
            "V1.29R is the first true kickoff artifact for the post-commercial-aerospace board worker.",
            "BK0480 now moves from transfer memo into its own local role-grammar phase under an explicit local-reset rule.",
        ]
        return V129RBK0480AerospaceAviationTransferWorkerKickoffTriageReport(
            summary=summary,
            direction_rows=direction_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129RBK0480AerospaceAviationTransferWorkerKickoffTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129RBK0480AerospaceAviationTransferWorkerKickoffTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129r_bk0480_aerospace_aviation_transfer_worker_kickoff_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
