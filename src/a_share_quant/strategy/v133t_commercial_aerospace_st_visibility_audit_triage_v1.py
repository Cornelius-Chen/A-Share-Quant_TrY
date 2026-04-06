from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133TCommercialAerospaceSTVisibilityAuditTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V133TCommercialAerospaceSTVisibilityAuditTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v133s_commercial_aerospace_point_in_time_visibility_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_st_visibility_audit_triage_v1.csv"
        )

    def analyze(self) -> V133TCommercialAerospaceSTVisibilityAuditTriageReport:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        summary = audit["summary"]
        all_zero = (
            summary["same_bar_violation_count"] == 0
            and summary["path_cutoff_violation_count"] == 0
            and summary["lineage_monotonic_violation_count"] == 0
            and summary["event_visibility_violation_count"] == 0
            and summary["warmup_nonnull_violation_count"] == 0
        )

        triage_rows = [
            {
                "component": "canonical_seed_visibility_feed",
                "status": "accepted_for_phase_1_extension" if all_zero else "blocked",
                "rationale": "canonical seed feed passes the point-in-time legality audit and can now serve as the reference surface for broader visibility work",
            },
            {
                "component": "broader_minute_surface_extension",
                "status": "next_allowed_move" if all_zero else "blocked",
                "rationale": "broader visibility extension is only lawful after the canonical seed feed proves same-bar and lineage discipline",
            },
            {
                "component": "simulator_buildout",
                "status": "still_blocked",
                "rationale": "even with a passed seed visibility audit, simulator work remains downstream of broader phase-1 extension",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        report_summary = {
            "acceptance_posture": "freeze_v133t_commercial_aerospace_st_visibility_audit_triage_v1",
            "seed_session_count": summary["seed_session_count"],
            "authoritative_status": "accept_canonical_seed_visibility_feed_and_allow_broader_phase_1_extension_only" if all_zero else "block_phase_1_extension",
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.33T translates the canonical seed visibility audit into an explicit direction decision.",
            "A passed seed audit does not unlock simulation; it only permits phase-1 visibility to widen carefully.",
        ]
        return V133TCommercialAerospaceSTVisibilityAuditTriageReport(
            summary=report_summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133TCommercialAerospaceSTVisibilityAuditTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133TCommercialAerospaceSTVisibilityAuditTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133t_commercial_aerospace_st_visibility_audit_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
