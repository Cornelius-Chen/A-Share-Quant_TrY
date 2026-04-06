from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134po_a_share_replay_market_context_residual_fixability_audit_v1 import (
    V134POAShareReplayMarketContextResidualFixabilityAuditV1Analyzer,
)


@dataclass(slots=True)
class V134PQASharePOMarketContextFixabilityDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134PQASharePOMarketContextFixabilityDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134PQASharePOMarketContextFixabilityDirectionTriageV1Report:
        report = V134POAShareReplayMarketContextResidualFixabilityAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "residual_count": report.summary["residual_count"],
            "external_boundary_count": report.summary["external_boundary_count"],
            "internal_calendar_alignment_count": report.summary["internal_calendar_alignment_count"],
            "authoritative_status": "replay_market_context_residuals_should_split_into_boundary_retention_and_small_internal_calendar_inspection",
        }
        triage_rows = [
            {
                "component": "external_boundary_residuals",
                "direction": "retain_pre_coverage_residuals_as_boundary_exceptions_not_as_current_build_failures",
            },
            {
                "component": "internal_calendar_alignment_candidate",
                "direction": "inspect_the_single_off_calendar_shadow_slice_before_freezing_it_as_hard_residual",
            },
            {
                "component": "replay_governance",
                "direction": "do_not_reopen_execution_but_allow_a_narrow_shadow_calendar_alignment_check",
            },
        ]
        interpretation = [
            "The residual set is now small enough to separate immutable boundary residue from one potentially fixable shadow-input issue.",
            "That means the next replay move should be a narrow calendar-alignment inspection, not another broad market-context rebuild.",
        ]
        return V134PQASharePOMarketContextFixabilityDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PQASharePOMarketContextFixabilityDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PQASharePOMarketContextFixabilityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pq_a_share_po_market_context_fixability_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
