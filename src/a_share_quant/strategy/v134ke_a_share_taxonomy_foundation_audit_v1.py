from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.taxonomy.pipelines.materialize_a_share_taxonomy_foundation_v1 import (
    MaterializeAShareTaxonomyFoundationV1,
)


@dataclass(slots=True)
class V134KEAShareTaxonomyFoundationAuditV1Report:
    summary: dict[str, Any]
    taxonomy_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "taxonomy_rows": self.taxonomy_rows,
            "interpretation": self.interpretation,
        }


class V134KEAShareTaxonomyFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_taxonomy_foundation_status_v1.csv"

    def analyze(self) -> V134KEAShareTaxonomyFoundationAuditV1Report:
        materialized = MaterializeAShareTaxonomyFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        taxonomy_rows = [
            {
                "taxonomy_component": "concept_membership",
                "component_state": "materialized_partial_foundation",
                "artifact_path": summary["concept_output_path"],
                "coverage_note": f"concept_covered_symbol_count = {summary['concept_covered_symbol_count']}",
            },
            {
                "taxonomy_component": "sector_membership",
                "component_state": "materialized_partial_foundation",
                "artifact_path": summary["sector_output_path"],
                "coverage_note": f"sector_covered_symbol_count = {summary['sector_covered_symbol_count']}",
            },
            {
                "taxonomy_component": "business_reference",
                "component_state": "backlog_materialized_not_filled",
                "artifact_path": summary["business_reference_backlog_path"],
                "coverage_note": f"business_reference_backlog_count = {summary['business_reference_backlog_count']}",
            },
            {
                "taxonomy_component": "concept_purity",
                "component_state": "backlog_materialized_not_filled",
                "artifact_path": summary["concept_purity_backlog_path"],
                "coverage_note": f"concept_purity_backlog_count = {summary['concept_purity_backlog_count']}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(taxonomy_rows[0].keys()))
            writer.writeheader()
            writer.writerows(taxonomy_rows)

        report_summary = {
            "acceptance_posture": "build_v134ke_a_share_taxonomy_foundation_audit_v1",
            "identity_symbol_count": summary["identity_symbol_count"],
            "concept_membership_row_count": summary["concept_membership_row_count"],
            "sector_membership_row_count": summary["sector_membership_row_count"],
            "concept_covered_symbol_count": summary["concept_covered_symbol_count"],
            "sector_covered_symbol_count": summary["sector_covered_symbol_count"],
            "taxonomy_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_taxonomy_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34KE completes the first taxonomy workstream pass by materializing concept and sector memberships on top of the canonical identity layer.",
            "Business reference and concept purity are not faked; they are explicitly turned into backlog registries so the taxonomy class can remain honest and still stay operationally complete.",
        ]
        return V134KEAShareTaxonomyFoundationAuditV1Report(
            summary=report_summary,
            taxonomy_rows=taxonomy_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KEAShareTaxonomyFoundationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KEAShareTaxonomyFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ke_a_share_taxonomy_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
