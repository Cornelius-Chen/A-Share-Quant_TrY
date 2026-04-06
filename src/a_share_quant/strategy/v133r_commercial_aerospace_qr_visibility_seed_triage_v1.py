from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133RCommercialAerospaceQRVisibilitySeedTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V133RCommercialAerospaceQRVisibilitySeedTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.feed_report_path = (
            repo_root / "reports" / "analysis" / "v133q_commercial_aerospace_point_in_time_seed_feed_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_qr_visibility_seed_triage_v1.csv"
        )

    def analyze(self) -> V133RCommercialAerospaceQRVisibilitySeedTriageReport:
        feed_report = json.loads(self.feed_report_path.read_text(encoding="utf-8"))

        lineage_ok = feed_report["summary"]["lineage_null_count"] == 0

        triage_rows = [
            {
                "component": "canonical_seed_point_in_time_feed",
                "status": "retain_as_phase_1_seed_surface" if lineage_ok else "blocked",
                "rationale": "the canonical seed feed now exists with explicit first-visible lineage and lagged-only path features",
            },
            {
                "component": "broader_session_expansion",
                "status": "blocked_until_seed_visibility_audit_extends",
                "rationale": "the first lawful move is to stabilize canonical seeds before widening to broader minute sessions",
            },
            {
                "component": "simulator_buildout",
                "status": "blocked_until_visibility_seed_surface_is_accepted",
                "rationale": "simulator work must remain downstream of a passed point-in-time visibility seed surface",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v133r_commercial_aerospace_qr_visibility_seed_triage_v1",
            "seed_session_count": feed_report["summary"]["seed_session_count"],
            "feed_row_count": feed_report["summary"]["feed_row_count"],
            "authoritative_status": "retain_phase_1_visibility_seed_surface_and_keep_later_phases_blocked",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.33R turns the canonical point-in-time seed feed into an explicit triage state.",
            "The branch may continue inside phase_1_visibility, but only on the seed surface and without opening simulator or replay work.",
        ]
        return V133RCommercialAerospaceQRVisibilitySeedTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133RCommercialAerospaceQRVisibilitySeedTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133RCommercialAerospaceQRVisibilitySeedTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133r_commercial_aerospace_qr_visibility_seed_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
