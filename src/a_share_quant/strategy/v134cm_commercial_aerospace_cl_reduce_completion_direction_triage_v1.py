from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CMCommercialAerospaceCLReduceCompletionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134CMCommercialAerospaceCLReduceCompletionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.status_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134cl_commercial_aerospace_reduce_completion_status_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_cl_reduce_completion_direction_triage_v1.csv"
        )

    def analyze(self) -> V134CMCommercialAerospaceCLReduceCompletionDirectionTriageV1Report:
        status = json.loads(self.status_path.read_text(encoding="utf-8"))
        summary = status["summary"]

        triage_rows = [
            {
                "component": "reduce_mainline_research",
                "status": "complete_enough_to_freeze",
                "detail": (
                    f"sell_side_binding_reference_ready = {summary['sell_side_binding_reference_ready']}, "
                    f"broad_reduce_tuning_stopped = {summary['broad_reduce_tuning_stopped']}"
                ),
            },
            {
                "component": "remaining_work",
                "status": "residue_maintenance_only",
                "detail": (
                    f"local_residue_supervision_only = {summary['local_residue_supervision_only']}, "
                    f"residue_seed_count = {summary['residue_seed_count']}"
                ),
            },
            {
                "component": "execution_closure",
                "status": "still_infrastructure_blocked",
                "detail": f"remaining_execution_blocker_count = {summary['remaining_execution_blocker_count']}",
            },
            {
                "component": "next_research_frontier",
                "status": "do_not_switch_inside_this_step_but_reduce_is_ready_for_handoff",
                "detail": "Reduce mainline research can now be considered frozen; any future effort should either stay local-residue only or wait for the later handoff to intraday add.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        report_summary = {
            "acceptance_posture": "freeze_v134cm_commercial_aerospace_cl_reduce_completion_direction_triage_v1",
            "authoritative_status": "freeze_reduce_mainline_as_research_complete_and_leave_only_local_residue_maintenance",
            "remaining_execution_blocker_count": summary["remaining_execution_blocker_count"],
            "residue_seed_count": summary["residue_seed_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CM turns the reduce completion audit into a final direction judgment for the mainline research branch.",
            "The correct reading is not that execution is solved. The correct reading is that broad reduce research is now finished enough to freeze, leaving only local residue maintenance under supervision.",
        ]
        return V134CMCommercialAerospaceCLReduceCompletionDirectionTriageV1Report(
            summary=report_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CMCommercialAerospaceCLReduceCompletionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CMCommercialAerospaceCLReduceCompletionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cm_commercial_aerospace_cl_reduce_completion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
