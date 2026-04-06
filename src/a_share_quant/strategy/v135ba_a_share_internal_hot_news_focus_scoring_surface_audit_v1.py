from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_focus_scoring_surface_v1 import (
    MaterializeAShareInternalHotNewsFocusScoringSurfaceV1,
)


@dataclass(slots=True)
class V135BAAShareInternalHotNewsFocusScoringSurfaceAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135BAAShareInternalHotNewsFocusScoringSurfaceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135BAAShareInternalHotNewsFocusScoringSurfaceAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsFocusScoringSurfaceV1(self.repo_root).materialize()
        rows = [
            {
                "component": "focus_scoring_surface",
                "component_state": "materialized",
                "metric": "scored_row_count",
                "value": str(materialized.summary["scored_row_count"]),
            },
            {
                "component": "focus_scoring_surface",
                "component_state": "materialized",
                "metric": "top_theme_slug",
                "value": materialized.summary["top_theme_slug"],
            },
            {
                "component": "focus_scoring_surface",
                "component_state": "materialized",
                "metric": "top_focus_total_score",
                "value": f"{materialized.summary['top_focus_total_score']:.4f}",
            },
            {
                "component": "focus_scoring_surface",
                "component_state": "materialized",
                "metric": "top_cycle_state",
                "value": materialized.summary["top_cycle_state"],
            },
        ]
        interpretation = [
            "This scoring surface converts raw support counts into trading-aware focus scores.",
            "The score blends source authority, policy-like wording, cycle persistence, second-wave retrigger potential, crowding exhaustion, and tradability.",
            "It is the new scoring backbone for leaderboard and challenger review, so high-policy persistent themes can outrank exhausted one-spike themes even at similar support counts.",
        ]
        return V135BAAShareInternalHotNewsFocusScoringSurfaceAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135BAAShareInternalHotNewsFocusScoringSurfaceAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135BAAShareInternalHotNewsFocusScoringSurfaceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ba_a_share_internal_hot_news_focus_scoring_surface_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
