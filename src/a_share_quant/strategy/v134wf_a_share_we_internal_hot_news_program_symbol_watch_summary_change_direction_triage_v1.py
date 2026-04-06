from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134we_a_share_internal_hot_news_program_symbol_watch_summary_change_signal_audit_v1 import (
    V134WEAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V134WFAShareWEInternalHotNewsProgramSymbolWatchSummaryChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134WFAShareWEInternalHotNewsProgramSymbolWatchSummaryChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134WFAShareWEInternalHotNewsProgramSymbolWatchSummaryChangeDirectionTriageV1Report:
        report = V134WEAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "change_row_count": report.summary["change_row_count"],
            "top_watch_symbol_change": report.summary["top_watch_symbol_change"],
            "top_watch_bundle_change": report.summary["top_watch_bundle_change"],
            "top_watch_theme_change": report.summary["top_watch_theme_change"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "continue_serving_symbol-level_change_signals_to_symbol-first_consumers",
        }
        triage_rows = [
            {
                "component": "stable_symbol_watch_branch",
                "direction": "keep_lightweight_symbol_watch_polling_when_the_symbol_watch_change_signal_stays_stable",
            },
            {
                "component": "rotating_symbol_watch_branch",
                "direction": "refresh_symbol-level_watch_routing_when_the_top_watch_symbol_or_top-five_bundle_changes",
            },
        ]
        interpretation = [
            "This is the highest-value symbol-level change signal currently available on the hot-news line.",
            "A symbol-first consumer can use it to avoid reopening the symbol-watch summary unless the watchset actually rotates.",
        ]
        return V134WFAShareWEInternalHotNewsProgramSymbolWatchSummaryChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134WFAShareWEInternalHotNewsProgramSymbolWatchSummaryChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134WFAShareWEInternalHotNewsProgramSymbolWatchSummaryChangeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134wf_a_share_we_internal_hot_news_program_symbol_watch_summary_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
