from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134nc_a_share_paired_surface_extension_status_audit_v1 import (
    V134NCASharePairedSurfaceExtensionStatusAuditV1Analyzer,
)


@dataclass(slots=True)
class V134NDAShareNCPairedSurfaceDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134NDAShareNCPairedSurfaceDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134NDAShareNCPairedSurfaceDirectionTriageV1Report:
        report = V134NCASharePairedSurfaceExtensionStatusAuditV1Analyzer(self.repo_root).analyze()
        if report.summary["index_candidate_cover_count"] > 0 and report.summary["limit_halt_candidate_cover_count"] > 0:
            summary = {
                "index_candidate_cover_count": report.summary["index_candidate_cover_count"],
                "limit_halt_candidate_cover_count": report.summary["limit_halt_candidate_cover_count"],
                "authoritative_status": "paired_surface_candidate_layer_ready_for_promotion_recheck",
            }
            triage_rows = [
                {
                    "component": "index_daily_extension",
                    "direction": "retire_index_daily_as_primary_candidate_gap_blocker",
                },
                {
                    "component": "limit_halt_extension",
                    "direction": "shift_focus_to_limit_halt_materialization_and_promotion_recheck",
                },
            ]
            interpretation = [
                "The paired-surface blocker is no longer candidate-layer absence once both surfaces have cover.",
                "The next closure mode becomes promotion recheck rather than index-daily candidate search.",
            ]
        else:
            summary = {
                "index_candidate_cover_count": report.summary["index_candidate_cover_count"],
                "limit_halt_candidate_cover_count": report.summary["limit_halt_candidate_cover_count"],
                "authoritative_status": "paired_surface_extension_kept_blocked_by_index_daily_gap",
            }
            triage_rows = [
                {
                    "component": "index_daily_extension",
                    "direction": "treat_index_daily_as_primary_blocker_before_any_daily_market_promotion",
                },
                {
                    "component": "limit_halt_extension",
                    "direction": "retain_limit_halt_candidate_surface_as_ready_but_nonpromotive_until_index_daily_catches_up",
                },
            ]
            interpretation = [
                "The paired-surface blocker is no longer symmetric.",
                "Index-daily is now the dominant blocker; limit-halt has moved to a candidate-ready but still nonpromotive state.",
            ]
        return V134NDAShareNCPairedSurfaceDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NDAShareNCPairedSurfaceDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NDAShareNCPairedSurfaceDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nd_a_share_nc_paired_surface_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
