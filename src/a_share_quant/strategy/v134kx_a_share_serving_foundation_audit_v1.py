from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.serving.research.materialize_a_share_serving_foundation_v1 import (
    MaterializeAShareServingFoundationV1,
)


@dataclass(slots=True)
class V134KXAShareServingFoundationAuditV1Report:
    summary: dict[str, Any]
    serving_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "serving_rows": self.serving_rows,
            "interpretation": self.interpretation,
        }


class V134KXAShareServingFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_serving_foundation_status_v1.csv"

    def analyze(self) -> V134KXAShareServingFoundationAuditV1Report:
        materialized = MaterializeAShareServingFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        serving_rows = [
            {
                "serving_component": "research_views",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["research_path"],
                "coverage_note": f"research_view_count = {summary['research_view_count']}",
            },
            {
                "serving_component": "shadow_views",
                "component_state": "materialized_bootstrap_read_only",
                "artifact_path": summary["shadow_path"],
                "coverage_note": f"shadow_view_count = {summary['shadow_view_count']}",
            },
            {
                "serving_component": "live_like_views",
                "component_state": "deferred_backlog",
                "artifact_path": summary["live_like_path"],
                "coverage_note": f"live_like_view_count = {summary['live_like_view_count']}",
            },
            {
                "serving_component": "serving_routes",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["route_path"],
                "coverage_note": f"active_serving_route_count = {summary['active_serving_route_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(serving_rows[0].keys()))
            writer.writeheader()
            writer.writerows(serving_rows)

        report_summary = {
            "acceptance_posture": "build_v134kx_a_share_serving_foundation_audit_v1",
            "research_view_count": summary["research_view_count"],
            "shadow_view_count": summary["shadow_view_count"],
            "live_like_view_count": summary["live_like_view_count"],
            "active_serving_route_count": summary["active_serving_route_count"],
            "serving_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_serving_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34KX converts the previously built data-center layers into explicit research and shadow serving registries.",
            "Live-like serving remains consciously deferred, which preserves the separation between read-only replay and execution-adjacent consumption.",
        ]
        return V134KXAShareServingFoundationAuditV1Report(
            summary=report_summary,
            serving_rows=serving_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V134KXAShareServingFoundationAuditV1Report) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KXAShareServingFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kx_a_share_serving_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
