from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134DGCommercialAerospaceDFPrelaunchPlaybookV1Report:
    summary: dict[str, Any]
    playbook_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "playbook_rows": self.playbook_rows,
            "interpretation": self.interpretation,
        }


class V134DGCommercialAerospaceDFPrelaunchPlaybookV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.opening_checklist_path = analysis_dir / "v134cz_commercial_aerospace_intraday_add_opening_checklist_v1.json"
        self.heartbeat_path = analysis_dir / "v134df_commercial_aerospace_intraday_add_prelaunch_heartbeat_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_add_prelaunch_playbook_v1.csv"
        )

    def analyze(self) -> V134DGCommercialAerospaceDFPrelaunchPlaybookV1Report:
        opening_checklist = json.loads(self.opening_checklist_path.read_text(encoding="utf-8"))
        heartbeat = json.loads(self.heartbeat_path.read_text(encoding="utf-8"))

        playbook_rows = [
            {
                "step": "confirm_explicit_shift",
                "status": "required",
                "detail": "Do not open intraday add unless the frontier shift is explicit rather than implied by repeated continuation.",
            },
            {
                "step": "reconfirm_reduce_frozen",
                "status": "required",
                "detail": "Reduce must remain frozen_mainline with only local residue supervision allowed.",
            },
            {
                "step": "reassert_board_veto_stack",
                "status": "required",
                "detail": "Board lockout, local-only rebound guard, and revival unlock remain upstream even when add opens later.",
            },
            {
                "step": "open_as_supervision_only",
                "status": "required",
                "detail": "The first add frontier step must be supervision-only and may not claim execution authority.",
            },
            {
                "step": "refresh_program_master_status",
                "status": "required",
                "detail": "Update the program master card so the frontier changes from deferred to opened in a single deliberate move.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(playbook_rows[0].keys()))
            writer.writeheader()
            writer.writerows(playbook_rows)

        summary = {
            "acceptance_posture": "freeze_v134dg_commercial_aerospace_df_prelaunch_playbook_v1",
            "frontier_name": heartbeat["summary"]["frontier_name"],
            "frontier_state": heartbeat["summary"]["frontier_state"],
            "opening_gate_count": opening_checklist["summary"]["checklist_gate_count"],
            "playbook_step_count": len(playbook_rows),
            "playbook_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_add_prelaunch_playbook_ready_for_future_explicit_shift",
        }
        interpretation = [
            "V1.34DG turns the add-opening checklist into a shorter operational playbook for the later explicit shift.",
            "The playbook is intentionally procedural: it says how to open the frontier cleanly without letting deferred readiness become premature execution.",
        ]
        return V134DGCommercialAerospaceDFPrelaunchPlaybookV1Report(
            summary=summary,
            playbook_rows=playbook_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134DGCommercialAerospaceDFPrelaunchPlaybookV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134DGCommercialAerospaceDFPrelaunchPlaybookV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134dg_commercial_aerospace_df_prelaunch_playbook_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
