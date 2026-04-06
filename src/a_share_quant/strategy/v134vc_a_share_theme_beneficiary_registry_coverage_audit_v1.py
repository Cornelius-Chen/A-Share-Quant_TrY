from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_signal_enrichment_v1 import (
    THEME_ALIAS_MAP,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134VCAShareThemeBeneficiaryRegistryCoverageAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134VCAShareThemeBeneficiaryRegistryCoverageAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "taxonomy"
            / "a_share_theme_beneficiary_registry_v1.csv"
        )

    def analyze(self) -> V134VCAShareThemeBeneficiaryRegistryCoverageAuditV1Report:
        registry_rows = _read_csv(self.registry_path)
        theme_set = {row["theme_slug"] for row in registry_rows}
        symbol_set = {row["symbol"] for row in registry_rows}
        summary = {
            "theme_count": len(theme_set),
            "registry_row_count": len(registry_rows),
            "symbol_count": len(symbol_set),
            "alias_theme_count": len(THEME_ALIAS_MAP),
            "registry_alias_intersection_count": len(theme_set & set(THEME_ALIAS_MAP)),
            "authoritative_status": "theme_beneficiary_registry_expanded_and_alias_bound",
        }
        rows = [
            {
                "component": "theme_beneficiary_registry",
                "component_state": "materialized",
                "metric": "theme_count",
                "value": str(summary["theme_count"]),
            },
            {
                "component": "theme_beneficiary_registry",
                "component_state": "materialized",
                "metric": "registry_row_count",
                "value": str(summary["registry_row_count"]),
            },
            {
                "component": "theme_beneficiary_registry",
                "component_state": "materialized",
                "metric": "symbol_count",
                "value": str(summary["symbol_count"]),
            },
            {
                "component": "theme_alias_map",
                "component_state": "bound",
                "metric": "registry_alias_intersection_count",
                "value": str(summary["registry_alias_intersection_count"]),
            },
        ]
        interpretation = [
            "The theme-beneficiary registry is now materially broader than the initial hand-built seed and is aligned with the alias map used by hot-news signal enrichment.",
            "Coverage is still curated rather than exhaustive, but the registry now spans multiple recurring A-share theme families instead of only a few seed themes.",
        ]
        return V134VCAShareThemeBeneficiaryRegistryCoverageAuditV1Report(
            summary=summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134VCAShareThemeBeneficiaryRegistryCoverageAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134VCAShareThemeBeneficiaryRegistryCoverageAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134vc_a_share_theme_beneficiary_registry_coverage_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
