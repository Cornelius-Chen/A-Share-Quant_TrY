from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134va_a_share_internal_hot_news_opportunity_symbol_watch_surface_audit_v1 import (
    V134VAAShareInternalHotNewsOpportunitySymbolWatchSurfaceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134VBAShareVAInternalHotNewsOpportunitySymbolWatchDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134VBAShareVAInternalHotNewsOpportunitySymbolWatchDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134VBAShareVAInternalHotNewsOpportunitySymbolWatchDirectionTriageV1Report:
        report = V134VAAShareInternalHotNewsOpportunitySymbolWatchSurfaceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "symbol_watch_row_count": report.summary["symbol_watch_row_count"],
            "unique_symbol_count": report.summary["unique_symbol_count"],
            "opportunity_event_count": report.summary["opportunity_event_count"],
            "top_symbol": report.summary["top_symbol"],
            "top_theme": report.summary["top_theme"],
            "top_mapping_confidence": report.summary["top_mapping_confidence"],
            "top_linkage_class": report.summary["top_linkage_class"],
            "authoritative_status": "continue_serving_symbol_level_opportunity_watch_rows_downstream",
        }
        triage_rows = [
            {
                "component": "symbol_level_consumer",
                "direction": "prefer_this_surface_when_the_consumer_needs_a_ready_to_route_symbol_watchlist_instead_of_a_theme-level_opportunity_row",
            },
            {
                "component": "theme_level_consumer",
                "direction": "stay_on_the_opportunity_feed_when_the_consumer_only_needs_theme-level_priority_and_gate_information",
            },
        ]
        interpretation = [
            "This surface is a downstream convenience layer under the opportunity feed, not a replacement for the higher-level routing views.",
            "Its purpose is to let a trading consumer move directly from opportunity events to symbol watch rows with no string parsing.",
            "The theme carried here is already the governed primary theme, so symbol-level consumers do not need to resolve overlap again.",
        ]
        return V134VBAShareVAInternalHotNewsOpportunitySymbolWatchDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134VBAShareVAInternalHotNewsOpportunitySymbolWatchDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134VBAShareVAInternalHotNewsOpportunitySymbolWatchDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134vb_a_share_va_internal_hot_news_opportunity_symbol_watch_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
