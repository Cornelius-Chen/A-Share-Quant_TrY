from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130HTransferProgramGHSamePlaneFreezeTriageReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V130HTransferProgramGHSamePlaneFreezeTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.freeze_path = repo_root / "reports" / "analysis" / "v130g_transfer_program_same_plane_support_freeze_v1.json"

    def analyze(self) -> V130HTransferProgramGHSamePlaneFreezeTriageReport:
        freeze = json.loads(self.freeze_path.read_text(encoding="utf-8"))
        direction_rows = [
            {
                "direction": "new_board_worker",
                "status": "blocked",
                "reason": "No queued board currently has a multi-symbol same-plane surface strong enough for lawful transfer preparation.",
            },
            {
                "direction": "bk0808_shadow_worker",
                "status": "blocked",
                "reason": "BK0808 collapses to a single-symbol v6 surface, so a worker would be pseudo-board research rather than transferable board work.",
            },
            {
                "direction": "transfer_program_state",
                "status": "freeze",
                "reason": "The transfer program should pause here rather than degrade methodology quality.",
            },
            {
                "direction": "next_primary_direction",
                "status": "wait_for_richer_same_plane_support_then_reopen_board_selection",
                "reason": "The next valid trigger is new same-plane local support, not more queue speculation.",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v130h_transfer_program_gh_same_plane_freeze_triage_v1",
            "same_plane_ready_count": freeze["summary"]["same_plane_ready_count"],
            "bridge_only_count": freeze["summary"]["bridge_only_count"],
            "authoritative_status": "freeze_transfer_program_and_do_not_open_a_new_board_worker_yet",
            "authoritative_rule": "maintain_transfer_discipline_even_if_that_means_pausing_after_commercial_aerospace_and_bk0480",
        }
        interpretation = [
            "V1.30H freezes the transfer queue after confirming that every remaining candidate is too thin for the methodology we just proved on commercial aerospace.",
            "Pausing is preferable to manufacturing a false sense of cross-board progress from single-symbol boards.",
        ]
        return V130HTransferProgramGHSamePlaneFreezeTriageReport(
            summary=summary,
            direction_rows=direction_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V130HTransferProgramGHSamePlaneFreezeTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130HTransferProgramGHSamePlaneFreezeTriageAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130h_transfer_program_gh_same_plane_freeze_triage_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
