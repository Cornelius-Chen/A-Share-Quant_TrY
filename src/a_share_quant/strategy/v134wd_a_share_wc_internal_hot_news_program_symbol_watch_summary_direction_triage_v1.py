from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134wc_a_share_internal_hot_news_program_symbol_watch_summary_audit_v1 import (
    V134WCAShareInternalHotNewsProgramSymbolWatchSummaryAuditV1Analyzer,
)


@dataclass(slots=True)
class V134WDAShareWCInternalHotNewsProgramSymbolWatchSummaryDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134WDAShareWCInternalHotNewsProgramSymbolWatchSummaryDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134WDAShareWCInternalHotNewsProgramSymbolWatchSummaryDirectionTriageV1Report:
        report = V134WCAShareInternalHotNewsProgramSymbolWatchSummaryAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "summary_row_count": report.summary["summary_row_count"],
            "watchlist_row_count": report.summary["watchlist_row_count"],
            "top_watch_symbol": report.summary["top_watch_symbol"],
            "top_watch_primary_theme_slug": report.summary["top_watch_primary_theme_slug"],
            "top_watch_mapping_confidence": report.summary["top_watch_mapping_confidence"],
            "top_watch_linkage_class": report.summary["top_watch_linkage_class"],
            "top_watch_symbols_top5": report.summary["top_watch_symbols_top5"],
            "authoritative_status": "continue_serving_single-row_symbol_watch_summary_to_fast_symbol-first_consumers",
        }
        triage_rows = [
            {
                "component": "fast_symbol_consumer",
                "direction": "prefer_this_summary_when_the_consumer_wants_the_top_watch_symbols_without_opening_the_full_watchlist_packet",
            },
            {
                "component": "full_symbol_consumer",
                "direction": "fall_back_to_the_symbol_watchlist_packet_when_rank-by-rank_symbol_rows_or_richer_fields_are_needed",
            },
        ]
        interpretation = [
            "This summary is the fastest symbol-level opportunity entrypoint built so far on the hot-news line.",
            "It keeps the first-pass watch decision on one row while preserving a path back to the fuller symbol watchlist packet.",
            "The top-five payload is governed by primary-theme logic, so the consumer does not need to re-resolve overlap at summary time.",
        ]
        return V134WDAShareWCInternalHotNewsProgramSymbolWatchSummaryDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134WDAShareWCInternalHotNewsProgramSymbolWatchSummaryDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134WDAShareWCInternalHotNewsProgramSymbolWatchSummaryDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134wd_a_share_wc_internal_hot_news_program_symbol_watch_summary_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
