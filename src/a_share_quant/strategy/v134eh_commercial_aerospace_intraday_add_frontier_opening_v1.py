from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134EHCommercialAerospaceIntradayAddFrontierOpeningV1Report:
    summary: dict[str, Any]
    opening_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "opening_rows": self.opening_rows,
            "interpretation": self.interpretation,
        }


class V134EHCommercialAerospaceIntradayAddFrontierOpeningV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.checklist_path = analysis_dir / "v134cz_commercial_aerospace_intraday_add_opening_checklist_v1.json"
        self.playbook_path = analysis_dir / "v134dg_commercial_aerospace_df_prelaunch_playbook_v1.json"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_add_frontier_opening_v1.csv"
        )

    def analyze(self) -> V134EHCommercialAerospaceIntradayAddFrontierOpeningV1Report:
        checklist = json.loads(self.checklist_path.read_text(encoding="utf-8"))
        playbook = json.loads(self.playbook_path.read_text(encoding="utf-8"))

        opening_rows = [
            {
                "opening_stage": "explicit_frontier_shift",
                "status": "executed_now",
                "detail": "The current user continuation is treated as the explicit shift that opens intraday add research.",
            },
            {
                "opening_stage": "frontier_scope",
                "status": "supervision_only",
                "detail": "Intraday add opens as a supervision frontier, not as an execution-facing or replay-facing branch.",
            },
            {
                "opening_stage": "upstream_veto_stack",
                "status": "retained",
                "detail": "Board cooling lockout, local-only rebound guard, and board revival unlock remain upstream constraints.",
            },
            {
                "opening_stage": "reduce_authority",
                "status": "not_inherited",
                "detail": "Intraday add does not inherit reduce execution authority or reopen reduce frozen mainline.",
            },
            {
                "opening_stage": "first_build_step",
                "status": "approved",
                "detail": "The first add artifact should be an intraday add supervision registry rather than an execution rule or replay lane.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(opening_rows[0].keys()))
            writer.writeheader()
            writer.writerows(opening_rows)

        summary = {
            "acceptance_posture": "open_v134eh_commercial_aerospace_intraday_add_frontier_opening_v1",
            "opening_gate_count": checklist["summary"]["checklist_gate_count"],
            "playbook_step_count": playbook["summary"]["playbook_step_count"],
            "frontier_name": "intraday_add",
            "frontier_state": "opened_supervision_only",
            "first_build_step": "intraday_add_supervision_registry_v1",
            "opening_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_add_frontier_opening_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34EH is the explicit frontier shift: intraday add is no longer deferred, but it only opens as a supervision frontier.",
            "The opening is intentionally narrow so the branch can begin without inheriting reduce execution claims or bypassing board-level vetoes.",
        ]
        return V134EHCommercialAerospaceIntradayAddFrontierOpeningV1Report(
            summary=summary,
            opening_rows=opening_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EHCommercialAerospaceIntradayAddFrontierOpeningV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EHCommercialAerospaceIntradayAddFrontierOpeningV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134eh_commercial_aerospace_intraday_add_frontier_opening_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
