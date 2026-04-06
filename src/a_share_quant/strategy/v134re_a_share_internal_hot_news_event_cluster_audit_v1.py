from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_event_cluster_v1 import (
    MaterializeAShareInternalHotNewsEventClusterV1,
)


@dataclass(slots=True)
class V134REAShareInternalHotNewsEventClusterAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134REAShareInternalHotNewsEventClusterAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134REAShareInternalHotNewsEventClusterAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsEventClusterV1(self.repo_root).materialize()
        rows = [
            {
                "component": "event_cluster_surface",
                "component_state": "materialized",
                "metric": "cluster_row_count",
                "value": str(materialized.summary["cluster_row_count"]),
            },
            {
                "component": "deduped_event_stream",
                "component_state": "read_ready_internal_only",
                "metric": "deduped_row_count",
                "value": str(materialized.summary["deduped_row_count"]),
            },
            {
                "component": "duplicate_reduction",
                "component_state": "measured",
                "metric": "duplicate_reduction_count",
                "value": str(materialized.summary["duplicate_reduction_count"]),
            },
        ]
        interpretation = [
            "The hot-news lane now materializes event clusters before downstream trading consumption.",
            "The trading layer can read a deduped event stream instead of consuming every raw telegraph row as an independent event.",
        ]
        return V134REAShareInternalHotNewsEventClusterAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134REAShareInternalHotNewsEventClusterAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134REAShareInternalHotNewsEventClusterAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134re_a_share_internal_hot_news_event_cluster_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
