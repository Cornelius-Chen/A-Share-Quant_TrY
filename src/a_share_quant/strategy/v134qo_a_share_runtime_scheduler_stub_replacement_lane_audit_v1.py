from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qg_a_share_runtime_promotion_candidate_surface_audit_v1 import (
    V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Report:
    summary: dict[str, Any]
    lane_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "lane_rows": self.lane_rows, "interpretation": self.interpretation}


class V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_runtime_scheduler_stub_replacement_lane_v1.csv"
        )
        self.excluded_output_csv = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_runtime_scheduler_stub_replacement_lane_excluded_v1.csv"
        )

    def analyze(self) -> V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Report:
        candidate_report = V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer(self.repo_root).analyze()

        lane_rows = []
        excluded_rows = []
        for row in candidate_report.rows:
            if row["candidate_class"] == "priority_runtime_candidate":
                lane_rows.append(
                    {
                        "adapter_id": row["adapter_id"],
                        "queue_priority": row["queue_priority"],
                        "candidate_state": row["candidate_state"],
                        "lane_state": "scheduler_stub_replacement_lane_materialized",
                        "activation_mode": "shadow-like_internal_source_runtime_lane_only",
                        "blocking_reason": row["blocking_reason"],
                    }
                )
            else:
                excluded_rows.append(
                    {
                        "adapter_id": row["adapter_id"],
                        "candidate_class": row["candidate_class"],
                        "excluded_reason": row["blocking_reason"],
                    }
                )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(lane_rows[0].keys()))
            writer.writeheader()
            writer.writerows(lane_rows)

        with self.excluded_output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(excluded_rows[0].keys()))
            writer.writeheader()
            writer.writerows(excluded_rows)

        summary = {
            "lane_row_count": len(lane_rows),
            "excluded_row_count": len(excluded_rows),
            "authoritative_output": "a_share_runtime_scheduler_stub_replacement_lane_materialized",
        }
        interpretation = [
            "Source-side runtime followthrough now has a single scheduler-stub replacement lane instead of only a checklist.",
            "Excluded adapters remain outside this lane, so progress stays narrow and controlled.",
        ]
        return V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Report(
            summary=summary, lane_rows=lane_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qo_a_share_runtime_scheduler_stub_replacement_lane_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
