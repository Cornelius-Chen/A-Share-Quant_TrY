from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_symbol_watch_summary_change_signal_v1 import (
    MaterializeAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalV1,
)


@dataclass(slots=True)
class V134WEAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134WEAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134WEAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalV1(self.repo_root).materialize()
        rows = [
            {
                "component": "symbol_watch_summary_change_signal",
                "component_state": "read_ready_internal_only",
                "metric": "change_row_count",
                "value": str(materialized.summary["change_row_count"]),
            },
            {
                "component": "top_watch_symbol_change",
                "component_state": "materialized",
                "metric": "top_watch_symbol_change",
                "value": materialized.summary["top_watch_symbol_change"],
            },
            {
                "component": "top_watch_bundle_change",
                "component_state": "materialized",
                "metric": "top_watch_bundle_change",
                "value": materialized.summary["top_watch_bundle_change"],
            },
            {
                "component": "top_watch_theme_change",
                "component_state": "materialized",
                "metric": "top_watch_theme_change",
                "value": materialized.summary["top_watch_theme_change"],
            },
            {
                "component": "signal_priority",
                "component_state": "materialized",
                "metric": "signal_priority",
                "value": materialized.summary["signal_priority"],
            },
        ]
        interpretation = [
            "This change layer is the symbol-first counterpart to the higher-level snapshot and control-packet change signals.",
            "It only elevates when the top watch symbol, the top-five symbol bundle, or the top watch theme actually rotates.",
        ]
        return V134WEAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134WEAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134WEAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134we_a_share_internal_hot_news_program_symbol_watch_summary_change_signal_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
