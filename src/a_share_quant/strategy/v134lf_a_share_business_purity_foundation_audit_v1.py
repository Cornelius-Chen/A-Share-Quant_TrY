from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.taxonomy.materialize_a_share_business_purity_foundation_v1 import (
    MaterializeAShareBusinessPurityFoundationV1,
)


@dataclass(slots=True)
class V134LFAShareBusinessPurityFoundationAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134LFAShareBusinessPurityFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_business_purity_foundation_status_v1.csv"

    def analyze(self) -> V134LFAShareBusinessPurityFoundationAuditV1Report:
        materialized = MaterializeAShareBusinessPurityFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "business_reference",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["business_path"],
                "coverage_note": f"business_reference_count = {summary['business_reference_count']}",
            },
            {
                "component": "concept_purity",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["purity_path"],
                "coverage_note": f"concept_purity_count = {summary['concept_purity_count']}",
            },
            {
                "component": "residual_backlog",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": f"residual_count = {summary['residual_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "acceptance_posture": "build_v134lf_a_share_business_purity_foundation_audit_v1",
            "business_reference_count": summary["business_reference_count"],
            "concept_purity_count": summary["concept_purity_count"],
            "sector_backed_with_concepts_count": summary["sector_backed_with_concepts_count"],
            "mixed_multi_theme_count": summary["mixed_multi_theme_count"],
            "residual_count": summary["residual_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_business_purity_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "This closes the first honest business-reference and concept-purity gap using only in-repo sector and concept surfaces, without inventing external fundamentals.",
            "The output is strong enough for reusable tagging, while residuals remain explicit wherever sector or concept support is structurally thin.",
        ]
        return V134LFAShareBusinessPurityFoundationAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LFAShareBusinessPurityFoundationAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LFAShareBusinessPurityFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lf_a_share_business_purity_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
