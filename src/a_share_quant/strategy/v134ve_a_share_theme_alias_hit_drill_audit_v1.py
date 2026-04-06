from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_theme_alias_hit_drill_v1 import (
    MaterializeAShareThemeAliasHitDrillV1,
)


@dataclass(slots=True)
class V134VEAShareThemeAliasHitDrillAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134VEAShareThemeAliasHitDrillAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134VEAShareThemeAliasHitDrillAuditV1Report:
        materialized = MaterializeAShareThemeAliasHitDrillV1(self.repo_root).materialize()
        rows = [
            {
                "component": "theme_alias_hit_drill",
                "component_state": "materialized",
                "metric": "case_count",
                "value": str(materialized.summary["case_count"]),
            },
            {
                "component": "theme_alias_hit_drill",
                "component_state": "measured",
                "metric": "exact_expected_hit_count",
                "value": str(materialized.summary["exact_expected_hit_count"]),
            },
            {
                "component": "theme_alias_hit_drill",
                "component_state": "measured",
                "metric": "expected_covered_count",
                "value": str(materialized.summary["expected_covered_count"]),
            },
            {
                "component": "theme_alias_hit_drill",
                "component_state": "measured",
                "metric": "overlap_hit_count",
                "value": str(materialized.summary["overlap_hit_count"]),
            },
            {
                "component": "theme_alias_hit_drill",
                "component_state": "measured",
                "metric": "partial_or_miss_count",
                "value": str(materialized.summary["partial_or_miss_count"]),
            },
        ]
        interpretation = [
            "This drill validates that the current alias map can actually hit the curated theme families in simulated news headlines.",
            "Overlap is acceptable when the expected theme is still covered; the drill is testing reachability, not enforcing single-label purity.",
        ]
        return V134VEAShareThemeAliasHitDrillAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134VEAShareThemeAliasHitDrillAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134VEAShareThemeAliasHitDrillAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ve_a_share_theme_alias_hit_drill_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
