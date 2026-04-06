from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_accepted_rotation_shadow_snapshot_v1 import (
    MaterializeAShareInternalHotNewsAcceptedRotationShadowSnapshotV1,
)


@dataclass(slots=True)
class V134ZOAShareInternalHotNewsAcceptedRotationShadowSnapshotAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134ZOAShareInternalHotNewsAcceptedRotationShadowSnapshotAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZOAShareInternalHotNewsAcceptedRotationShadowSnapshotAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsAcceptedRotationShadowSnapshotV1(self.repo_root).materialize()
        rows = [
            {
                "component": "shadow_snapshot",
                "component_state": "materialized",
                "metric": "current_top_opportunity_theme",
                "value": materialized.summary["current_top_opportunity_theme"],
            },
            {
                "component": "shadow_snapshot",
                "component_state": "materialized",
                "metric": "shadow_top_opportunity_theme",
                "value": materialized.summary["shadow_top_opportunity_theme"],
            },
            {
                "component": "shadow_snapshot",
                "component_state": "materialized",
                "metric": "current_top_watch_symbol",
                "value": materialized.summary["current_top_watch_symbol"],
            },
            {
                "component": "shadow_snapshot",
                "component_state": "materialized",
                "metric": "shadow_top_watch_symbol",
                "value": materialized.summary["shadow_top_watch_symbol"],
            },
        ]
        interpretation = [
            "This shadow snapshot shows the top-level consumer state after accepting the rotation, without mutating the live primary snapshot.",
            "It is the closest shadow analogue of the accepted post-rotation state.",
        ]
        return V134ZOAShareInternalHotNewsAcceptedRotationShadowSnapshotAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZOAShareInternalHotNewsAcceptedRotationShadowSnapshotAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZOAShareInternalHotNewsAcceptedRotationShadowSnapshotAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zo_a_share_internal_hot_news_accepted_rotation_shadow_snapshot_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
