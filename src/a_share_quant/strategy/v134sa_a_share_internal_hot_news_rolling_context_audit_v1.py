from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_rolling_context_v1 import (
    MaterializeAShareInternalHotNewsRollingContextV1,
)


@dataclass(slots=True)
class V134SAAShareInternalHotNewsRollingContextAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SAAShareInternalHotNewsRollingContextAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SAAShareInternalHotNewsRollingContextAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsRollingContextV1(self.repo_root).materialize()
        rows = [
            {
                "component": "rolling_context_surface",
                "component_state": "materialized",
                "metric": "context_row_count",
                "value": str(materialized.summary["context_row_count"]),
            },
            {
                "component": "important_impact_window",
                "component_state": "materialized",
                "metric": "important_impact_row_count",
                "value": str(materialized.summary["important_impact_row_count"]),
            },
            {
                "component": "active_impact_window",
                "component_state": "measured",
                "metric": "active_impact_count",
                "value": str(materialized.summary["active_impact_count"]),
            },
            {
                "component": "context_velocity",
                "component_state": "materialized",
                "metric": "accelerating_context_count",
                "value": str(materialized.summary["accelerating_context_count"]),
            },
            {
                "component": "context_cooling",
                "component_state": "materialized",
                "metric": "cooling_context_count",
                "value": str(materialized.summary["cooling_context_count"]),
            },
        ]
        interpretation = [
            "The hot-news lane now emits rolling context rows instead of forcing the consumer to reason over isolated message rows only.",
            "Important messages also carry a separate impact-window surface so the trading layer can remember them beyond the raw hot-news sequence.",
            "Rolling context now includes recent-60m/recent-180m counts, recency-weighted signal scores, and explicit velocity/cooling states.",
        ]
        return V134SAAShareInternalHotNewsRollingContextAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SAAShareInternalHotNewsRollingContextAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SAAShareInternalHotNewsRollingContextAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sa_a_share_internal_hot_news_rolling_context_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
