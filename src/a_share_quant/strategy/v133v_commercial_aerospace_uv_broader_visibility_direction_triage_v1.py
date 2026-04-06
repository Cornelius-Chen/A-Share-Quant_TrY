from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133VCommercialAerospaceUVBroaderVisibilityDirectionTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V133VCommercialAerospaceUVBroaderVisibilityDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.broader_feed_path = (
            repo_root / "reports" / "analysis" / "v133u_commercial_aerospace_point_in_time_broader_hit_feed_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_uv_broader_visibility_direction_triage_v1.csv"
        )

    def analyze(self) -> V133VCommercialAerospaceUVBroaderVisibilityDirectionTriageReport:
        broader_feed = json.loads(self.broader_feed_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "broader_hit_point_in_time_feed",
                "status": "retain_as_phase_1_extension_surface",
                "rationale": "the wider 24-session surface now exists with the same first-visible lineage discipline as the seed surface",
            },
            {
                "component": "all_session_visibility_expansion",
                "status": "blocked_until_broader_hit_audit",
                "rationale": "the next lawful check is whether the broader-hit surface still obeys phase-1 visibility rules before widening further",
            },
            {
                "component": "simulator_buildout",
                "status": "still_blocked",
                "rationale": "visibility can widen inside phase 1, but simulator work remains downstream and closed",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v133v_commercial_aerospace_uv_broader_visibility_direction_triage_v1",
            "broader_hit_session_count": broader_feed["summary"]["broader_hit_session_count"],
            "feed_row_count": broader_feed["summary"]["feed_row_count"],
            "authoritative_status": "retain_broader_phase_1_visibility_surface_and_keep_simulator_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.33V confirms that phase_1_visibility may widen from canonical seeds to broader hit sessions without opening later workstreams.",
            "The simulator and replay lanes remain closed; the only allowed motion is further legality audit inside phase 1.",
        ]
        return V133VCommercialAerospaceUVBroaderVisibilityDirectionTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133VCommercialAerospaceUVBroaderVisibilityDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133VCommercialAerospaceUVBroaderVisibilityDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133v_commercial_aerospace_uv_broader_visibility_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
