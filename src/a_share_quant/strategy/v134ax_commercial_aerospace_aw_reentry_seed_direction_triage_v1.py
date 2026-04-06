from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AXCommercialAerospaceAWReentrySeedDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134AXCommercialAerospaceAWReentrySeedDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root / "reports" / "analysis" / "v134aw_commercial_aerospace_post_exit_reentry_seed_registry_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_aw_reentry_seed_direction_triage_v1.csv"
        )

    def analyze(self) -> V134AXCommercialAerospaceAWReentrySeedDirectionTriageV1Report:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "post_exit_reentry_seed_registry",
                "status": "frozen",
                "detail": (
                    f"registry_count = {registry['summary']['registry_count']}, dominant_reentry_family = {registry['summary']['dominant_reentry_family']}"
                ),
            },
            {
                "component": "next_supervision_build",
                "status": "approved_for_seed_level_reentry_supervision",
                "detail": "The next work should stay at seed-level and define rebuild/reentry supervision labels before any simulator work.",
            },
            {
                "component": "replay_lane",
                "status": "still_blocked",
                "detail": "Reentry seeds are only a new supervision family, not a replay-facing lane.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134ax_commercial_aerospace_aw_reentry_seed_direction_triage_v1",
            "authoritative_status": "freeze_reentry_seed_registry_and_shift_next_to_seed_level_reentry_supervision",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34AX turns the new post-exit reentry seed registry into the next supervised direction.",
            "The branch should move from sell-side refinement to seed-level rebuild timing supervision without touching replay boundaries.",
        ]
        return V134AXCommercialAerospaceAWReentrySeedDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AXCommercialAerospaceAWReentrySeedDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AXCommercialAerospaceAWReentrySeedDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ax_commercial_aerospace_aw_reentry_seed_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
