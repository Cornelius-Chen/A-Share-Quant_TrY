from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ya_a_share_theme_beneficiary_mapping_quality_summary_audit_v1 import (
    V134YAAShareThemeBeneficiaryMappingQualitySummaryAuditV1Analyzer,
)


@dataclass(slots=True)
class V134YBAShareYAThemeBeneficiaryMappingQualityDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134YBAShareYAThemeBeneficiaryMappingQualityDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134YBAShareYAThemeBeneficiaryMappingQualityDirectionTriageV1Report:
        report = V134YAAShareThemeBeneficiaryMappingQualitySummaryAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "theme_count": report.summary["theme_count"],
            "direct_row_count": report.summary["direct_row_count"],
            "proxy_row_count": report.summary["proxy_row_count"],
            "weak_row_count": report.summary["weak_row_count"],
            "direct_clean_theme_count": report.summary["direct_clean_theme_count"],
            "proxy_heavy_theme_count": report.summary["proxy_heavy_theme_count"],
            "weak_exposed_theme_count": report.summary["weak_exposed_theme_count"],
            "authoritative_status": "continue_strengthening_proxy-heavy_and_weak-exposed_themes_before_expanding_more_long-tail_mappings",
        }
        triage_rows = [
            {
                "component": "direct_clean_themes",
                "direction": "treat direct-clean themes as the highest-trust symbol-routing layer for the trading consumer",
            },
            {
                "component": "proxy_heavy_themes",
                "direction": "prefer watch and confirmation handling on proxy-heavy themes unless stronger direct beneficiaries are curated",
            },
            {
                "component": "weak_exposed_themes",
                "direction": "prioritize weak-exposed themes for curation cleanup before using them as high-trust symbol-level routing evidence",
            },
        ]
        interpretation = [
            "The next improvement step is now obvious: clean weak-exposed themes and reduce proxy-heavy dependence where possible.",
            "This summary is a quicker planning surface than scanning raw beneficiary rows one by one.",
        ]
        return V134YBAShareYAThemeBeneficiaryMappingQualityDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134YBAShareYAThemeBeneficiaryMappingQualityDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134YBAShareYAThemeBeneficiaryMappingQualityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134yb_a_share_ya_theme_beneficiary_mapping_quality_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
