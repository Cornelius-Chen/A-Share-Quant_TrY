from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_symbol_watch_summary_v1 import (
    MaterializeAShareInternalHotNewsProgramSymbolWatchSummaryV1,
)


@dataclass(slots=True)
class V134WCAShareInternalHotNewsProgramSymbolWatchSummaryAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134WCAShareInternalHotNewsProgramSymbolWatchSummaryAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134WCAShareInternalHotNewsProgramSymbolWatchSummaryAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramSymbolWatchSummaryV1(self.repo_root).materialize()
        rows = [
            {
                "component": "program_symbol_watch_summary",
                "component_state": "read_ready_internal_only",
                "metric": "summary_row_count",
                "value": str(materialized.summary["summary_row_count"]),
            },
            {
                "component": "watchlist_coverage",
                "component_state": "materialized",
                "metric": "watchlist_row_count",
                "value": str(materialized.summary["watchlist_row_count"]),
            },
            {
                "component": "top_watch_symbol",
                "component_state": "materialized",
                "metric": "top_watch_symbol",
                "value": materialized.summary["top_watch_symbol"],
            },
            {
                "component": "top_watch_theme",
                "component_state": "materialized",
                "metric": "top_watch_primary_theme_slug",
                "value": materialized.summary["top_watch_primary_theme_slug"],
            },
            {
                "component": "top_watch_bundle",
                "component_state": "materialized",
                "metric": "top_watch_symbols_top5",
                "value": materialized.summary["top_watch_symbols_top5"],
            },
            {
                "component": "top_watch_linkage",
                "component_state": "materialized",
                "metric": "top_watch_linkage_class",
                "value": materialized.summary["top_watch_linkage_class"],
            },
        ]
        interpretation = [
            "This summary compresses the symbol watchlist packet into a single-row payload for fast polling consumers.",
            "It preserves the top watch symbol plus a top-five bundle, so the consumer can stay on one row for the first routing pass.",
            "It also exposes linkage class, so direct beneficiaries can be separated from weaker proxies at summary level.",
            "Primary-theme governance remains visible at the summary layer, keeping overlap handling below the consumer boundary.",
        ]
        return V134WCAShareInternalHotNewsProgramSymbolWatchSummaryAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134WCAShareInternalHotNewsProgramSymbolWatchSummaryAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134WCAShareInternalHotNewsProgramSymbolWatchSummaryAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134wc_a_share_internal_hot_news_program_symbol_watch_summary_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
