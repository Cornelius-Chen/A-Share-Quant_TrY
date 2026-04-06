from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ke_a_share_taxonomy_foundation_audit_v1 import (
    V134KEAShareTaxonomyFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134KFAShareKETaxonomyDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KFAShareKETaxonomyDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134KFAShareKETaxonomyDirectionTriageV1Report:
        audit = V134KEAShareTaxonomyFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "taxonomy_component": "concept_membership",
                "direction": "retain_as_current_concept_surface_and_expand_coverage_later_without_reopening_identity",
            },
            {
                "taxonomy_component": "sector_membership",
                "direction": "retain_as_current_sector_surface_and use_as_business_reference_context_seed",
            },
            {
                "taxonomy_component": "business_reference",
                "direction": "fill_backlog_symbol_by_symbol_using_canonical_identity_and current taxonomy context",
            },
            {
                "taxonomy_component": "concept_purity",
                "direction": "fill_backlog_after_business_reference_so_purity_is_judged_against_real_business anchors",
            },
            {
                "taxonomy_component": "next_frontier",
                "direction": "move_into_business_reference_population_without_reopening_identity_or_faking_purity_labels",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134kf_a_share_ke_taxonomy_direction_triage_v1",
            "concept_covered_symbol_count": audit.summary["concept_covered_symbol_count"],
            "sector_covered_symbol_count": audit.summary["sector_covered_symbol_count"],
            "authoritative_status": "taxonomy_foundation_complete_enough_to_freeze_and_shift_into_business_reference_population",
        }
        interpretation = [
            "V1.34KF converts the taxonomy audit into operating direction.",
            "The correct next move is not to fake concept purity now; it is to use current concept and sector surfaces as context while filling business-reference backlog first.",
        ]
        return V134KFAShareKETaxonomyDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KFAShareKETaxonomyDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KFAShareKETaxonomyDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kf_a_share_ke_taxonomy_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
