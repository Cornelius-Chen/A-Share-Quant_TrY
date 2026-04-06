from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AZCommercialAerospaceAYReentrySupervisionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134AZCommercialAerospaceAYReentrySupervisionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.spec_path = (
            repo_root / "reports" / "analysis" / "v134ay_commercial_aerospace_post_exit_reentry_supervision_spec_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_ay_reentry_supervision_direction_triage_v1.csv"
        )

    def analyze(self) -> V134AZCommercialAerospaceAYReentrySupervisionDirectionTriageV1Report:
        spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        dominant_family = spec["summary"]["dominant_family"]

        triage_rows = [
            {
                "component": "post_exit_reentry_supervision_spec",
                "status": "frozen",
                "detail": f"seed_count = {spec['summary']['seed_count']}, dominant_family = {dominant_family}",
            },
            {
                "component": "next_supervision_build",
                "status": "approved_for_seed_level_reentry_supervision",
                "detail": "Continue with seed-level rebuild timing supervision before any simulation or replay work.",
            },
            {
                "component": "reentry_simulator_lane",
                "status": "still_blocked",
                "detail": "No reentry simulator or replay lane is authorized from seed labels alone.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134az_commercial_aerospace_ay_reentry_supervision_direction_triage_v1",
            "authoritative_status": "freeze_reentry_supervision_spec_and_continue_seed_level_reentry_supervision",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AZ converts the new reentry supervision spec into the next direction judgment.",
            "The branch should move into seed-level reentry supervision, but still must not build replay-facing execution from these labels yet.",
        ]
        return V134AZCommercialAerospaceAYReentrySupervisionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AZCommercialAerospaceAYReentrySupervisionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AZCommercialAerospaceAYReentrySupervisionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134az_commercial_aerospace_ay_reentry_supervision_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
