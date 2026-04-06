from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_symbol_watchlist_packet_v1 import (
    MaterializeAShareInternalHotNewsProgramSymbolWatchlistPacketV1,
)


@dataclass(slots=True)
class V134WAAShareInternalHotNewsProgramSymbolWatchlistPacketAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134WAAShareInternalHotNewsProgramSymbolWatchlistPacketAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134WAAShareInternalHotNewsProgramSymbolWatchlistPacketAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramSymbolWatchlistPacketV1(self.repo_root).materialize()
        rows = [
            {
                "component": "program_symbol_watchlist_packet",
                "component_state": "read_ready_internal_only",
                "metric": "watchlist_row_count",
                "value": str(materialized.summary["watchlist_row_count"]),
            },
            {
                "component": "unique_symbols",
                "component_state": "materialized",
                "metric": "unique_symbol_count",
                "value": str(materialized.summary["unique_symbol_count"]),
            },
            {
                "component": "top_watch_symbol",
                "component_state": "materialized",
                "metric": "top_watch_symbol",
                "value": materialized.summary["top_watch_symbol"],
            },
            {
                "component": "top_primary_theme",
                "component_state": "materialized",
                "metric": "top_primary_theme_slug",
                "value": materialized.summary["top_primary_theme_slug"],
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
        ]
        interpretation = [
            "This packet converts the symbol watch surface into a program-facing watchlist that is already deduplicated by symbol.",
            "The top-ranked symbol now carries the governed primary theme, so downstream watch consumers do not need to repeat overlap resolution.",
            "It also exposes linkage class so the consumer can distinguish direct beneficiaries from weaker proxies.",
            "This is the most direct symbol-level opportunity packet under the current internal hot-news pipeline.",
        ]
        return V134WAAShareInternalHotNewsProgramSymbolWatchlistPacketAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134WAAShareInternalHotNewsProgramSymbolWatchlistPacketAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134WAAShareInternalHotNewsProgramSymbolWatchlistPacketAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134wa_a_share_internal_hot_news_program_symbol_watchlist_packet_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
