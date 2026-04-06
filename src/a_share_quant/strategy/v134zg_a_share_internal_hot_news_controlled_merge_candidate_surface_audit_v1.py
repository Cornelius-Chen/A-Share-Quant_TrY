from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_controlled_merge_candidate_surface_v1 import (
    MaterializeAShareInternalHotNewsControlledMergeCandidateSurfaceV1,
)


@dataclass(slots=True)
class V134ZGAShareInternalHotNewsControlledMergeCandidateSurfaceAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134ZGAShareInternalHotNewsControlledMergeCandidateSurfaceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZGAShareInternalHotNewsControlledMergeCandidateSurfaceAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsControlledMergeCandidateSurfaceV1(self.repo_root).materialize()
        rows = [
            {
                "component": "candidate_surface",
                "component_state": "materialized",
                "metric": "candidate_row_count",
                "value": str(materialized.summary["candidate_row_count"]),
            },
            {
                "component": "candidate_surface",
                "component_state": "materialized",
                "metric": "cls_primary_count",
                "value": str(materialized.summary["cls_primary_count"]),
            },
            {
                "component": "candidate_surface",
                "component_state": "materialized",
                "metric": "sina_additive_count",
                "value": str(materialized.summary["sina_additive_count"]),
            },
            {
                "component": "coverage",
                "component_state": "measured",
                "metric": "unique_theme_count",
                "value": str(materialized.summary["unique_theme_count"]),
            },
            {
                "component": "coverage",
                "component_state": "measured",
                "metric": "unique_symbol_count",
                "value": str(materialized.summary["unique_symbol_count"]),
            },
        ]
        interpretation = [
            "This candidate surface keeps the cls primary line intact while exposing additive second-source themed rows.",
            "It is a controlled merge lane, not a direct fastlane promotion.",
        ]
        return V134ZGAShareInternalHotNewsControlledMergeCandidateSurfaceAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZGAShareInternalHotNewsControlledMergeCandidateSurfaceAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZGAShareInternalHotNewsControlledMergeCandidateSurfaceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zg_a_share_internal_hot_news_controlled_merge_candidate_surface_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
