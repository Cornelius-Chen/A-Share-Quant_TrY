from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134na_a_share_index_daily_extension_candidate_audit_v1 import (
    V134NAAShareIndexDailyExtensionCandidateAuditV1Analyzer,
)
from a_share_quant.strategy.v134nb_a_share_limit_halt_extension_candidate_audit_v1 import (
    V134NBAShareLimitHaltExtensionCandidateAuditV1Analyzer,
)


@dataclass(slots=True)
class V134NCASharePairedSurfaceExtensionStatusAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134NCASharePairedSurfaceExtensionStatusAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134NCASharePairedSurfaceExtensionStatusAuditV1Report:
        index_report = V134NAAShareIndexDailyExtensionCandidateAuditV1Analyzer(self.repo_root).analyze()
        limit_report = V134NBAShareLimitHaltExtensionCandidateAuditV1Analyzer(self.repo_root).analyze()

        rows = [
            {
                "paired_surface": "index_daily",
                "candidate_cover_count": index_report.summary["candidate_cover_count"],
                "paired_surface_state": (
                    "candidate_available" if index_report.summary["candidate_cover_count"] > 0 else "candidate_missing"
                ),
            },
            {
                "paired_surface": "limit_halt",
                "candidate_cover_count": limit_report.summary["candidate_cover_count"],
                "paired_surface_state": (
                    "candidate_available" if limit_report.summary["candidate_cover_count"] > 0 else "candidate_missing"
                ),
            },
        ]
        summary = {
            "index_candidate_cover_count": index_report.summary["candidate_cover_count"],
            "limit_halt_candidate_cover_count": limit_report.summary["candidate_cover_count"],
            "authoritative_output": "a_share_paired_surface_extension_status_explicit",
        }
        if index_report.summary["candidate_cover_count"] > 0 and limit_report.summary["candidate_cover_count"] > 0:
            interpretation = [
                "Paired surfaces are now separated cleanly instead of being bundled into one blocker.",
                "Both candidate layers are now present, so the next replay-side question moves from candidate absence to promotion and derivation readiness.",
            ]
        else:
            interpretation = [
                "Paired surfaces are now separated cleanly instead of being bundled into one blocker.",
                "Current stopline is asymmetric: limit-halt has candidate cover, index-daily does not.",
            ]
        return V134NCASharePairedSurfaceExtensionStatusAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NCASharePairedSurfaceExtensionStatusAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NCASharePairedSurfaceExtensionStatusAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nc_a_share_paired_surface_extension_status_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
