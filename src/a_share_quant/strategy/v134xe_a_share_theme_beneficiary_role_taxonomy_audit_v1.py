from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_theme_beneficiary_role_taxonomy_v1 import (
    MaterializeAShareThemeBeneficiaryRoleTaxonomyV1,
)


@dataclass(slots=True)
class V134XEAShareThemeBeneficiaryRoleTaxonomyAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134XEAShareThemeBeneficiaryRoleTaxonomyAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134XEAShareThemeBeneficiaryRoleTaxonomyAuditV1Report:
        materialized = MaterializeAShareThemeBeneficiaryRoleTaxonomyV1(self.repo_root).materialize()
        rows = [
            {
                "component": "beneficiary_role_taxonomy",
                "component_state": "materialized",
                "metric": "role_variant_count",
                "value": str(materialized.summary["role_variant_count"]),
            },
            {
                "component": "beneficiary_role_taxonomy",
                "component_state": "materialized",
                "metric": "normalized_role_family_count",
                "value": str(materialized.summary["normalized_role_family_count"]),
            },
            {
                "component": "beneficiary_role_taxonomy",
                "component_state": "materialized",
                "metric": "linkage_class_count",
                "value": str(materialized.summary["linkage_class_count"]),
            },
        ]
        interpretation = [
            "The raw beneficiary-role strings are now normalized into a smaller taxonomy so downstream consumers do not depend on ad hoc adjacent_* variants.",
            "Linkage class is now an intentional taxonomy output rather than an inline string heuristic only.",
        ]
        return V134XEAShareThemeBeneficiaryRoleTaxonomyAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134XEAShareThemeBeneficiaryRoleTaxonomyAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134XEAShareThemeBeneficiaryRoleTaxonomyAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134xe_a_share_theme_beneficiary_role_taxonomy_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
