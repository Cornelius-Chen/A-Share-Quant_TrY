from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BJCommercialAerospaceBIHierarchyDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134BJCommercialAerospaceBIHierarchyDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.spec_path = (
            repo_root / "reports" / "analysis" / "v134bi_commercial_aerospace_hierarchy_governance_spec_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_bi_hierarchy_direction_triage_v1.csv"
        )

    def analyze(self) -> V134BJCommercialAerospaceBIHierarchyDirectionTriageV1Report:
        spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "board_cooling_lockout",
                "status": "retained_as_top_level_veto",
                "detail": "Cooling lockout remains the first decision layer once post-impulse board deterioration is confirmed.",
            },
            {
                "component": "local_only_rebound_guard",
                "status": "retained_as_explicit_false_bounce_guard",
                "detail": "A few strong rebound names inside weak breadth must not be upgraded into board revival.",
            },
            {
                "component": "board_revival_unlock",
                "status": "retained_as_only_release_discussion_gate",
                "detail": "Only broad board revival may release lockout discussion; isolated strength cannot.",
            },
            {
                "component": "seed_reentry_ladder",
                "status": "kept_subordinate",
                "detail": "Seed-level rebuild supervision regains meaning only after board-level unlock no longer vetoes it.",
            },
            {
                "component": "execution_binding",
                "status": "still_blocked",
                "detail": "Hierarchy remains governance-only and does not authorize replay or live intraday execution binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134bj_commercial_aerospace_bi_hierarchy_direction_triage_v1",
            "authoritative_status": "freeze_hierarchy_governance_spec_and_keep_board_first_governance_only",
            "hierarchy_level_count": spec["summary"]["hierarchy_level_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34BJ turns the hierarchy spec into a direction judgment.",
            "The branch should now reason board first: lockout, then anti-false-bounce guard, then unlock, and only then seed-level rebuild supervision.",
        ]
        return V134BJCommercialAerospaceBIHierarchyDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BJCommercialAerospaceBIHierarchyDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BJCommercialAerospaceBIHierarchyDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bj_commercial_aerospace_bi_hierarchy_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
