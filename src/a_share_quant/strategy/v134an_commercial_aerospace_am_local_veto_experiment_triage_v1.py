from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134ANCommercialAerospaceAMLocalVetoExperimentTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134ANCommercialAerospaceAMLocalVetoExperimentTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134am_commercial_aerospace_local_veto_experiment_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_am_local_veto_experiment_triage_v1.csv"
        )

    def analyze(self) -> V134ANCommercialAerospaceAMLocalVetoExperimentTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        same_day_delta = audit["summary"]["same_day_loss_avoided_delta_total"]
        rebound_saved = audit["summary"]["rebound_cost_saved_5d_total"]

        promote = rebound_saved > 0 and same_day_delta >= -1500
        triage_rows = [
            {
                "component": "local_rebound_cost_veto_experiment",
                "status": "promote_into_next_local_reference_test" if promote else "retain_as_supervision_only",
                "detail": f"same_day_delta = {same_day_delta}, rebound_cost_saved_5d = {rebound_saved}",
            },
            {
                "component": "phase2_wider_reference",
                "status": "unchanged_for_now",
                "detail": "The local veto experiment is judged separately before any stack update.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "This experiment remains local phase-2 supervision only.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134an_commercial_aerospace_am_local_veto_experiment_triage_v1",
            "authoritative_status": (
                "promote_local_veto_experiment_for_next_reference_test"
                if promote
                else "retain_local_veto_experiment_as_supervision_only"
            ),
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AN turns the first local veto experiment into the next supervision judgment.",
            "The branch should only carry the experiment forward if the saved rebound cost is positive and the same-day giveback remains bounded.",
        ]
        return V134ANCommercialAerospaceAMLocalVetoExperimentTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ANCommercialAerospaceAMLocalVetoExperimentTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ANCommercialAerospaceAMLocalVetoExperimentTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134an_commercial_aerospace_am_local_veto_experiment_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
