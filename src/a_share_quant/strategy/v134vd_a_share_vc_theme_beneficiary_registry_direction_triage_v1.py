from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134vc_a_share_theme_beneficiary_registry_coverage_audit_v1 import (
    V134VCAShareThemeBeneficiaryRegistryCoverageAuditV1Analyzer,
)


@dataclass(slots=True)
class V134VDAShareVCThemeBeneficiaryRegistryDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134VDAShareVCThemeBeneficiaryRegistryDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134VDAShareVCThemeBeneficiaryRegistryDirectionTriageV1Report:
        report = V134VCAShareThemeBeneficiaryRegistryCoverageAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "theme_count": report.summary["theme_count"],
            "registry_row_count": report.summary["registry_row_count"],
            "symbol_count": report.summary["symbol_count"],
            "alias_theme_count": report.summary["alias_theme_count"],
            "registry_alias_intersection_count": report.summary["registry_alias_intersection_count"],
            "authoritative_status": "continue_expanding_high-frequency_theme_families_before_chasing_long-tail_edge_themes",
        }
        triage_rows = [
            {
                "component": "high_frequency_theme_families",
                "direction": "keep_prioritizing themes that regularly appear in policy, macro, commodity, and technology news before chasing long-tail concept names",
            },
            {
                "component": "alias_binding",
                "direction": "expand alias coverage together with symbol mapping so registry growth can actually be reached by the hot-news classifier",
            },
            {
                "component": "symbol_watch_delivery",
                "direction": "prefer downstream symbol-level watch surfaces when beneficiary rows are already curated and avoid re-parsing theme strings in consumers",
            },
        ]
        interpretation = [
            "The registry is no longer a tiny seed; it is now a broader curated layer intended to catch common recurring A-share themes.",
            "The next gains should come from adding more high-frequency families and validating them against real incoming news, not from trying to enumerate every possible long-tail concept at once.",
        ]
        return V134VDAShareVCThemeBeneficiaryRegistryDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134VDAShareVCThemeBeneficiaryRegistryDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134VDAShareVCThemeBeneficiaryRegistryDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134vd_a_share_vc_theme_beneficiary_registry_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
