from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pm_a_share_replay_market_context_residual_classification_audit_v1 import (
    V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134PNASharePMMarketContextResidualDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134PNASharePMMarketContextResidualDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134PNASharePMMarketContextResidualDirectionTriageV1Report:
        report = V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "missing_residual_count": report.summary["missing_residual_count"],
            "pre_coverage_count": report.summary["pre_coverage_count"],
            "off_calendar_count": report.summary["off_calendar_count"],
            "authoritative_status": "replay_market_context_gap_reduced_to_boundary_and_calendar_residuals",
        }
        triage_rows = [
            {
                "component": "pre_coverage_residuals",
                "direction": "treat_pre_2024_shadow_slices_as_boundary_residuals_not_as_current_market-surface failures",
            },
            {
                "component": "off_calendar_residuals",
                "direction": "treat_off_calendar_shadow_slices_as_shadow-input anomalies_not_as_tradeable-context failures",
            },
            {
                "component": "replay_internal_build",
                "direction": "recheck_stub_and_live_like preconditions_under_the_narrowed_residual framing",
            },
        ]
        interpretation = [
            "The market-context gap has narrowed from a broad replay blocker to a small set of classified residuals.",
            "That supports moving the next replay narrative from coverage expansion toward boundary handling and precondition recheck.",
        ]
        return V134PNASharePMMarketContextResidualDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PNASharePMMarketContextResidualDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PNASharePMMarketContextResidualDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pn_a_share_pm_market_context_residual_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
