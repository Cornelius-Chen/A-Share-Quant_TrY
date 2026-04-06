from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_trade_calendar_bootstrap_v1 import (
    MaterializeAShareTradeCalendarBootstrapV1,
)


@dataclass(slots=True)
class V134SSAShareTradeCalendarBootstrapAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SSAShareTradeCalendarBootstrapAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SSAShareTradeCalendarBootstrapAuditV1Report:
        materialized = MaterializeAShareTradeCalendarBootstrapV1(self.repo_root).materialize()
        rows = [
            {
                "component": "trade_calendar_registry",
                "component_state": "materialized",
                "metric": "calendar_row_count",
                "value": str(materialized.summary["calendar_row_count"]),
            },
            {
                "component": "trade_calendar_coverage",
                "component_state": "materialized",
                "metric": "coverage_start",
                "value": materialized.summary["coverage_start"],
            },
            {
                "component": "trade_calendar_coverage",
                "component_state": "materialized",
                "metric": "coverage_end",
                "value": materialized.summary["coverage_end"],
            },
            {
                "component": "today_calendar_state",
                "component_state": "materialized",
                "metric": "today_calendar_state",
                "value": materialized.summary["today_calendar_state"],
            },
        ]
        interpretation = [
            "The internal hot-news status layer now has a real SSE trade calendar instead of weekday-only approximation.",
            "This closes the largest remaining timing approximation at the outermost program-status layer.",
        ]
        return V134SSAShareTradeCalendarBootstrapAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SSAShareTradeCalendarBootstrapAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SSAShareTradeCalendarBootstrapAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ss_a_share_trade_calendar_bootstrap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
