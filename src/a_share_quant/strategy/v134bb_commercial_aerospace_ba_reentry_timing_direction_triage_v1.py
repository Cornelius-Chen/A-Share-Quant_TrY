from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BBCommercialAerospaceBAReentryTimingDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134BBCommercialAerospaceBAReentryTimingDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134ba_commercial_aerospace_post_exit_reentry_timing_supervision_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_ba_reentry_timing_direction_triage_v1.csv"
        )

    def analyze(self) -> V134BBCommercialAerospaceBAReentryTimingDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        positive_1d_seed_count = int(audit["summary"]["positive_1d_seed_count"])
        positive_3d_seed_count = int(audit["summary"]["positive_3d_seed_count"])

        triage_rows = [
            {
                "component": "same_day_reentry",
                "status": "blocked",
                "detail": f"positive_1d_seed_count = {positive_1d_seed_count}; no seed authorizes same-day chase.",
            },
            {
                "component": "seed_level_reentry_timing_supervision",
                "status": "approved_to_continue",
                "detail": "Use the timing windows as supervision only before any simulator or replay-facing lane.",
            },
            {
                "component": "earliest_rebuild_watch",
                "status": "family_split_retained",
                "detail": (
                    "Delayed-rebound seeds may open rebuild watch from T+3; deep-washout seeds remain base-only until T+5. "
                    f"positive_3d_seed_count = {positive_3d_seed_count}."
                ),
            },
            {
                "component": "reentry_simulator_lane",
                "status": "still_blocked",
                "detail": "No reentry simulator is authorized from timing supervision alone.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134bb_commercial_aerospace_ba_reentry_timing_direction_triage_v1",
            "authoritative_status": "freeze_reentry_timing_supervision_and_continue_seed_level_timing_supervision",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34BB turns the new timing supervision audit into the next direction judgment.",
            "The branch may continue reentry timing supervision, but same-day chase and any simulator lane remain blocked.",
        ]
        return V134BBCommercialAerospaceBAReentryTimingDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BBCommercialAerospaceBAReentryTimingDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BBCommercialAerospaceBAReentryTimingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bb_commercial_aerospace_ba_reentry_timing_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
