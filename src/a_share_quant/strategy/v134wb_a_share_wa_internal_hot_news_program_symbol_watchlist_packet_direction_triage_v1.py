from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134wa_a_share_internal_hot_news_program_symbol_watchlist_packet_audit_v1 import (
    V134WAAShareInternalHotNewsProgramSymbolWatchlistPacketAuditV1Analyzer,
)


@dataclass(slots=True)
class V134WBAShareWAInternalHotNewsProgramSymbolWatchlistPacketDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134WBAShareWAInternalHotNewsProgramSymbolWatchlistPacketDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134WBAShareWAInternalHotNewsProgramSymbolWatchlistPacketDirectionTriageV1Report:
        report = V134WAAShareInternalHotNewsProgramSymbolWatchlistPacketAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "watchlist_row_count": report.summary["watchlist_row_count"],
            "unique_symbol_count": report.summary["unique_symbol_count"],
            "top_watch_symbol": report.summary["top_watch_symbol"],
            "top_primary_theme_slug": report.summary["top_primary_theme_slug"],
            "top_mapping_confidence": report.summary["top_mapping_confidence"],
            "top_linkage_class": report.summary["top_linkage_class"],
            "authoritative_status": "continue_serving_symbol-first_watchlist_packets_to_downstream_program_consumers",
        }
        triage_rows = [
            {
                "component": "symbol_watch_consumer",
                "direction": "prefer_this_packet_when_the_consumer_wants_a_ranked_symbol_watchlist_without_re-reading_theme-level_opportunity_rows",
            },
            {
                "component": "theme_watch_consumer",
                "direction": "stay_on_the_opportunity_feed_or_snapshot_when_only_theme-level_context_is_needed",
            },
        ]
        interpretation = [
            "This packet is narrower than the opportunity feed and more direct than the raw symbol watch surface.",
            "Its purpose is to provide a ranked symbol-first watchlist that is already governed by primary and secondary theme logic.",
            "Downstream consumers can treat this as the default opportunity watch entrypoint when they need symbol-level focus immediately.",
        ]
        return V134WBAShareWAInternalHotNewsProgramSymbolWatchlistPacketDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134WBAShareWAInternalHotNewsProgramSymbolWatchlistPacketDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134WBAShareWAInternalHotNewsProgramSymbolWatchlistPacketDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134wb_a_share_wa_internal_hot_news_program_symbol_watchlist_packet_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
