from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_opportunity_symbol_watch_surface_v1 import (
    MaterializeAShareInternalHotNewsOpportunitySymbolWatchSurfaceV1,
)


@dataclass(slots=True)
class V134VAAShareInternalHotNewsOpportunitySymbolWatchSurfaceAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134VAAShareInternalHotNewsOpportunitySymbolWatchSurfaceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134VAAShareInternalHotNewsOpportunitySymbolWatchSurfaceAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsOpportunitySymbolWatchSurfaceV1(self.repo_root).materialize()
        rows = [
            {
                "component": "opportunity_symbol_watch_surface",
                "component_state": "read_ready_internal_only",
                "metric": "symbol_watch_row_count",
                "value": str(materialized.summary["symbol_watch_row_count"]),
            },
            {
                "component": "unique_symbols",
                "component_state": "materialized",
                "metric": "unique_symbol_count",
                "value": str(materialized.summary["unique_symbol_count"]),
            },
            {
                "component": "opportunity_events",
                "component_state": "materialized",
                "metric": "opportunity_event_count",
                "value": str(materialized.summary["opportunity_event_count"]),
            },
            {
                "component": "top_mapping_confidence",
                "component_state": "materialized",
                "metric": "top_mapping_confidence",
                "value": materialized.summary["top_mapping_confidence"],
            },
            {
                "component": "top_linkage_class",
                "component_state": "materialized",
                "metric": "top_linkage_class",
                "value": materialized.summary["top_linkage_class"],
            },
            {
                "component": "top_theme",
                "component_state": "materialized",
                "metric": "top_theme",
                "value": materialized.summary["top_theme"],
            },
        ]
        interpretation = [
            "This surface explodes opportunity-feed beneficiary symbols into symbol-level watch rows for direct downstream consumption.",
            "The trading program no longer needs to split comma-separated beneficiary strings when it wants a symbol watchlist.",
            "The top symbol watch row now inherits the governed primary theme so overlap handling is already resolved before symbol-level delivery.",
            "It also carries linkage class so symbol-first consumers can distinguish direct beneficiaries from weaker proxies.",
        ]
        return V134VAAShareInternalHotNewsOpportunitySymbolWatchSurfaceAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134VAAShareInternalHotNewsOpportunitySymbolWatchSurfaceAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134VAAShareInternalHotNewsOpportunitySymbolWatchSurfaceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134va_a_share_internal_hot_news_opportunity_symbol_watch_surface_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
