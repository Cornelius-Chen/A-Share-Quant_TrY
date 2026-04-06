from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134TCommercialAerospaceSTPhase2CurrentDirectionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134TCommercialAerospaceSTPhase2CurrentDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.stack_path = analysis_dir / "v134s_commercial_aerospace_phase2_current_shadow_stack_v1.json"
        self.output_csv = repo_root / "data" / "training" / "commercial_aerospace_st_phase2_current_direction_triage_v1.csv"

    def analyze(self) -> V134TCommercialAerospaceSTPhase2CurrentDirectionTriageReport:
        stack = json.loads(self.stack_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "current_phase2_wider_reference",
                "status": "frozen",
                "detail": stack["summary"]["current_phase2_wider_reference"],
            },
            {
                "component": "next_optimization_direction",
                "status": "supervise_before_any_more_widening",
                "detail": "Use the mild-blocked broader-hit lane as the only wider reference and supervise it before any additional surface growth.",
            },
            {
                "component": "all_session_widening",
                "status": "still_blocked",
                "detail": "The branch is still not authorized to jump to all-session expansion.",
            },
            {
                "component": "phase3_replay_lane",
                "status": "still_blocked",
                "detail": "Phase-2 shadow progress still does not authorize replay binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134t_commercial_aerospace_st_phase2_current_direction_triage_v1",
            "authoritative_status": "freeze_current_phase2_shadow_stack_and_keep_all_session_and_replay_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34T converts the updated phase-2 shadow stack into the current direction judgment.",
            "The branch now has a current narrow reference and a current wider reference; no further widening is justified until the refined wider lane itself is supervised more deeply.",
        ]
        return V134TCommercialAerospaceSTPhase2CurrentDirectionTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TCommercialAerospaceSTPhase2CurrentDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TCommercialAerospaceSTPhase2CurrentDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134t_commercial_aerospace_st_phase2_current_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
