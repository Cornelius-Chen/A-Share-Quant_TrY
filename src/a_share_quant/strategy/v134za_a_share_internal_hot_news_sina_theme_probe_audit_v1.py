from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.ingest_jobs.fetch_a_share_internal_hot_news_sina_7x24_v1 import (
    FetchAShareInternalHotNewsSina7x24V1,
)
from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_sina_theme_probe_v1 import (
    MaterializeAShareInternalHotNewsSinaThemeProbeV1,
)


@dataclass(slots=True)
class V134ZAAShareInternalHotNewsSinaThemeProbeAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134ZAAShareInternalHotNewsSinaThemeProbeAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZAAShareInternalHotNewsSinaThemeProbeAuditV1Report:
        fetch_result = FetchAShareInternalHotNewsSina7x24V1(self.repo_root).materialize()
        probe_result = MaterializeAShareInternalHotNewsSinaThemeProbeV1(self.repo_root).materialize()
        rows = [
            {
                "component": "sina_probe_fetch",
                "component_state": "internal_only_probe_active",
                "metric": "fetch_row_count",
                "value": str(fetch_result.summary["fetch_row_count"]),
            },
            {
                "component": "sina_theme_probe",
                "component_state": "materialized",
                "metric": "theme_hit_count",
                "value": str(probe_result.summary["theme_hit_count"]),
            },
            {
                "component": "sina_theme_probe",
                "component_state": "materialized",
                "metric": "theme_hit_with_symbol_route_count",
                "value": str(probe_result.summary["theme_hit_with_symbol_route_count"]),
            },
            {
                "component": "sina_theme_probe",
                "component_state": "materialized",
                "metric": "unique_primary_theme_count",
                "value": str(probe_result.summary["unique_primary_theme_count"]),
            },
        ]
        summary = {
            "fetch_row_count": fetch_result.summary["fetch_row_count"],
            "sample_row_count": probe_result.summary["sample_row_count"],
            "broad_market_only_count": probe_result.summary["broad_market_only_count"],
            "theme_hit_count": probe_result.summary["theme_hit_count"],
            "theme_hit_with_symbol_route_count": probe_result.summary["theme_hit_with_symbol_route_count"],
            "unique_primary_theme_count": probe_result.summary["unique_primary_theme_count"],
            "authoritative_output": "a_share_internal_hot_news_sina_theme_probe_materialized",
        }
        interpretation = [
            "This probe tests whether a second live source increases real theme-hit density before merging it into the primary hot-news fastlane.",
            "It stays outside the main fastlane so source expansion can be measured without destabilizing the current trading-consumer surfaces.",
        ]
        return V134ZAAShareInternalHotNewsSinaThemeProbeAuditV1Report(
            summary=summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZAAShareInternalHotNewsSinaThemeProbeAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZAAShareInternalHotNewsSinaThemeProbeAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134za_a_share_internal_hot_news_sina_theme_probe_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
