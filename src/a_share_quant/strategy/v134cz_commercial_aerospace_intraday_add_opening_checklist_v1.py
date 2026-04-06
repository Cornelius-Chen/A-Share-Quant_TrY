from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CZCommercialAerospaceIntradayAddOpeningChecklistV1Report:
    summary: dict[str, Any]
    checklist_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "checklist_rows": self.checklist_rows,
            "interpretation": self.interpretation,
        }


class V134CZCommercialAerospaceIntradayAddOpeningChecklistV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.reduce_final_status_path = analysis_dir / "v134cv_commercial_aerospace_reduce_final_status_card_v1.json"
        self.transition_path = analysis_dir / "v134cq_commercial_aerospace_cp_transition_direction_triage_v1.json"
        self.program_status_path = analysis_dir / "v134cx_program_master_status_card_v2.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_add_opening_checklist_v1.csv"
        )

    def analyze(self) -> V134CZCommercialAerospaceIntradayAddOpeningChecklistV1Report:
        reduce_final_status = json.loads(self.reduce_final_status_path.read_text(encoding="utf-8"))
        transition = json.loads(self.transition_path.read_text(encoding="utf-8"))
        program_status = json.loads(self.program_status_path.read_text(encoding="utf-8"))

        checklist_rows = [
            {
                "opening_gate": "explicit_frontier_shift",
                "status": "mandatory",
                "detail": "Intraday add may open only after a deliberate frontier shift, not because reduce is already finished.",
            },
            {
                "opening_gate": "reduce_mainline_remains_frozen",
                "status": "mandatory",
                "detail": "Reduce must stay frozen_mainline and may not quietly reopen during add startup.",
            },
            {
                "opening_gate": "reduce_residue_stays_local_only",
                "status": "mandatory",
                "detail": "The four local rebound-residue seeds remain maintenance only and must not expand into fresh reduce tuning.",
            },
            {
                "opening_gate": "board_lockout_stays_upstream",
                "status": "mandatory",
                "detail": "Board cooling lockout remains an upstream veto before any intraday add exploration can claim permission.",
            },
            {
                "opening_gate": "local_only_rebound_guard_stays_upstream",
                "status": "mandatory",
                "detail": "Local-only rebound remains negative evidence and cannot be repackaged as add authorization.",
            },
            {
                "opening_gate": "board_revival_unlock_required_for_add_authority",
                "status": "mandatory",
                "detail": "Even after add research begins, board revival unlock is still required before any stronger authority claims.",
            },
            {
                "opening_gate": "add_starts_as_supervision_frontier",
                "status": "mandatory",
                "detail": "Intraday add opens as a new supervision frontier rather than an execution-facing lane.",
            },
            {
                "opening_gate": "no_reduce_execution_authority_inheritance",
                "status": "mandatory",
                "detail": "Intraday add must not inherit reduce execution authority or sell-side binding claims.",
            },
            {
                "opening_gate": "program_status_refresh",
                "status": "mandatory",
                "detail": "Program master status must be refreshed when the frontier eventually shifts from deferred to opened.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(checklist_rows[0].keys()))
            writer.writeheader()
            writer.writerows(checklist_rows)

        summary = {
            "acceptance_posture": "freeze_v134cz_commercial_aerospace_intraday_add_opening_checklist_v1",
            "reduce_status": next(
                row["value"] for row in reduce_final_status["status_rows"] if row["key"] == "reduce_status"
            ),
            "transition_status": transition["summary"]["authoritative_status"],
            "program_frontier_state": next(
                row["status"]
                for row in program_status["status_rows"]
                if row["program_line"] == "commercial_aerospace_next_frontier"
            ),
            "checklist_gate_count": len(checklist_rows),
            "checklist_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_add_opening_checklist_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34CZ does not open intraday add research; it formalizes the gates that must be respected when the later explicit shift happens.",
            "The checklist protects the program from accidentally treating add as a continuation of reduce or from bypassing the board-level veto stack.",
        ]
        return V134CZCommercialAerospaceIntradayAddOpeningChecklistV1Report(
            summary=summary,
            checklist_rows=checklist_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CZCommercialAerospaceIntradayAddOpeningChecklistV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CZCommercialAerospaceIntradayAddOpeningChecklistV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cz_commercial_aerospace_intraday_add_opening_checklist_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
