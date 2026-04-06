from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134xe_a_share_theme_beneficiary_role_taxonomy_audit_v1 import (
    V134XEAShareThemeBeneficiaryRoleTaxonomyAuditV1Analyzer,
)


@dataclass(slots=True)
class V134XFAShareXEThemeBeneficiaryRoleTaxonomyDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134XFAShareXEThemeBeneficiaryRoleTaxonomyDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134XFAShareXEThemeBeneficiaryRoleTaxonomyDirectionTriageV1Report:
        report = V134XEAShareThemeBeneficiaryRoleTaxonomyAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "role_variant_count": report.summary["role_variant_count"],
            "normalized_role_family_count": report.summary["normalized_role_family_count"],
            "linkage_class_count": report.summary["linkage_class_count"],
            "authoritative_status": "continue_serving_role-normalized_linkage_taxonomy_under_theme-to-symbol_mapping_quality",
        }
        triage_rows = [
            {
                "component": "role_normalization",
                "direction": "prefer_normalized_role_family_and_linkage_class_in_downstream_consumers_instead_of_raw_adjacent_* role strings",
            },
            {
                "component": "mapping_quality",
                "direction": "treat_direct_beneficiary_as_the_strongest symbol-routing class and proxy_or_weak classes as lower-trust watch evidence",
            },
        ]
        interpretation = [
            "The next mapping-quality work should build on this normalized taxonomy rather than expanding more raw role string variants.",
            "This gives downstream symbol-watch consumers a stable quality vocabulary while preserving the richer raw registry for curation work.",
        ]
        return V134XFAShareXEThemeBeneficiaryRoleTaxonomyDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134XFAShareXEThemeBeneficiaryRoleTaxonomyDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134XFAShareXEThemeBeneficiaryRoleTaxonomyDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134xf_a_share_xe_theme_beneficiary_role_taxonomy_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
