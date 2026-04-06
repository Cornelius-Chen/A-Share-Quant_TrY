from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_theme_overlap_governance_v1 import (
    MaterializeAShareThemeOverlapGovernanceV1,
)


@dataclass(slots=True)
class V134VGAShareThemeOverlapGovernanceAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134VGAShareThemeOverlapGovernanceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134VGAShareThemeOverlapGovernanceAuditV1Report:
        materialized = MaterializeAShareThemeOverlapGovernanceV1(self.repo_root).materialize()
        rows = [
            {
                "component": "overlap_governance_registry",
                "component_state": "materialized",
                "metric": "governance_rule_count",
                "value": str(materialized.summary["governance_rule_count"]),
            },
            {
                "component": "overlap_resolution_drill",
                "component_state": "materialized",
                "metric": "resolved_overlap_count",
                "value": str(materialized.summary["resolved_overlap_count"]),
            },
            {
                "component": "overlap_resolution_drill",
                "component_state": "measured",
                "metric": "unresolved_overlap_count",
                "value": str(materialized.summary["unresolved_overlap_count"]),
            },
        ]
        interpretation = [
            "This layer converts repeated multi-theme overlaps into explicit primary-vs-secondary governance instead of leaving them flat for downstream consumers.",
            "The first rules focus on recurring overlaps discovered by the alias hit drill.",
        ]
        return V134VGAShareThemeOverlapGovernanceAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134VGAShareThemeOverlapGovernanceAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134VGAShareThemeOverlapGovernanceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134vg_a_share_theme_overlap_governance_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
