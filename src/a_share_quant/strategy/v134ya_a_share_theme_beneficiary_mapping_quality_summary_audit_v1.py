from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_theme_beneficiary_mapping_quality_summary_v1 import (
    MaterializeAShareThemeBeneficiaryMappingQualitySummaryV1,
)


@dataclass(slots=True)
class V134YAAShareThemeBeneficiaryMappingQualitySummaryAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134YAAShareThemeBeneficiaryMappingQualitySummaryAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134YAAShareThemeBeneficiaryMappingQualitySummaryAuditV1Report:
        materialized = MaterializeAShareThemeBeneficiaryMappingQualitySummaryV1(self.repo_root).materialize()
        rows = [
            {
                "component": "mapping_quality_summary",
                "component_state": "materialized",
                "metric": "theme_count",
                "value": str(materialized.summary["theme_count"]),
            },
            {
                "component": "mapping_quality_summary",
                "component_state": "materialized",
                "metric": "direct_row_count",
                "value": str(materialized.summary["direct_row_count"]),
            },
            {
                "component": "mapping_quality_summary",
                "component_state": "materialized",
                "metric": "proxy_row_count",
                "value": str(materialized.summary["proxy_row_count"]),
            },
            {
                "component": "mapping_quality_summary",
                "component_state": "materialized",
                "metric": "weak_row_count",
                "value": str(materialized.summary["weak_row_count"]),
            },
            {
                "component": "mapping_quality_summary",
                "component_state": "materialized",
                "metric": "direct_clean_theme_count",
                "value": str(materialized.summary["direct_clean_theme_count"]),
            },
            {
                "component": "mapping_quality_summary",
                "component_state": "materialized",
                "metric": "proxy_heavy_theme_count",
                "value": str(materialized.summary["proxy_heavy_theme_count"]),
            },
            {
                "component": "mapping_quality_summary",
                "component_state": "materialized",
                "metric": "weak_exposed_theme_count",
                "value": str(materialized.summary["weak_exposed_theme_count"]),
            },
        ]
        interpretation = [
            "This summary compresses the curated theme-to-symbol registry into a quality overview by theme.",
            "It shows where the registry is already direct-led and where proxy or weak mappings still dominate.",
        ]
        return V134YAAShareThemeBeneficiaryMappingQualitySummaryAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134YAAShareThemeBeneficiaryMappingQualitySummaryAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134YAAShareThemeBeneficiaryMappingQualitySummaryAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ya_a_share_theme_beneficiary_mapping_quality_summary_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
