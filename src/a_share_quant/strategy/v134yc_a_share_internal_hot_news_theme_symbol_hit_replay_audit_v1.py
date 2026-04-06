from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_theme_symbol_hit_replay_v1 import (
    MaterializeAShareInternalHotNewsThemeSymbolHitReplayV1,
)


@dataclass(slots=True)
class V134YCAShareInternalHotNewsThemeSymbolHitReplayAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134YCAShareInternalHotNewsThemeSymbolHitReplayAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134YCAShareInternalHotNewsThemeSymbolHitReplayAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsThemeSymbolHitReplayV1(self.repo_root).materialize()
        rows = [
            {
                "component": "theme_symbol_hit_replay",
                "component_state": "materialized",
                "metric": "sample_row_count",
                "value": str(materialized.summary["sample_row_count"]),
            },
            {
                "component": "theme_symbol_hit_replay",
                "component_state": "materialized",
                "metric": "broad_market_only_count",
                "value": str(materialized.summary["broad_market_only_count"]),
            },
            {
                "component": "theme_symbol_hit_replay",
                "component_state": "materialized",
                "metric": "theme_hit_count",
                "value": str(materialized.summary["theme_hit_count"]),
            },
            {
                "component": "theme_symbol_hit_replay",
                "component_state": "materialized",
                "metric": "theme_hit_with_symbol_watch_count",
                "value": str(materialized.summary["theme_hit_with_symbol_watch_count"]),
            },
            {
                "component": "theme_symbol_hit_replay",
                "component_state": "materialized",
                "metric": "theme_hit_without_symbol_watch_count",
                "value": str(materialized.summary["theme_hit_without_symbol_watch_count"]),
            },
            {
                "component": "theme_symbol_hit_replay",
                "component_state": "materialized",
                "metric": "unique_primary_theme_count",
                "value": str(materialized.summary["unique_primary_theme_count"]),
            },
            {
                "component": "theme_symbol_hit_replay",
                "component_state": "materialized",
                "metric": "unique_watch_symbol_count",
                "value": str(materialized.summary["unique_watch_symbol_count"]),
            },
        ]
        interpretation = [
            "This replay summarizes what the current hot-news sample actually hit after theme governance and symbol mapping.",
            "It separates broad-market-only rows from theme-qualified rows and shows how many themed rows reached symbol watch.",
        ]
        return V134YCAShareInternalHotNewsThemeSymbolHitReplayAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134YCAShareInternalHotNewsThemeSymbolHitReplayAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134YCAShareInternalHotNewsThemeSymbolHitReplayAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134yc_a_share_internal_hot_news_theme_symbol_hit_replay_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
