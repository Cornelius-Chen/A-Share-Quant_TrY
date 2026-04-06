from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134nu_a_share_allowlist_promotion_precondition_surface_audit_v1 import (
    V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer,
)
from a_share_quant.strategy.v134qg_a_share_runtime_promotion_candidate_surface_audit_v1 import (
    V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer,
)
from a_share_quant.strategy.v134qk_a_share_runtime_scheduler_activation_precondition_audit_v1 import (
    V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_source_runtime_promotion_lane_status_v1.csv"
        )

    def analyze(self) -> V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Report:
        precondition_report = V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer(
            self.repo_root
        ).analyze()
        candidate_report = V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer(self.repo_root).analyze()
        scheduler_report = V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer(self.repo_root).analyze()

        rows = [
            {
                "runtime_component": "source_manual_closure",
                "runtime_state": "completed",
                "metric": "manual_review_preconditions_satisfied_count",
                "value": str(sum(row["precondition_state"] == "satisfied" for row in precondition_report.rows[:3])),
            },
            {
                "runtime_component": "first_runtime_candidate_lane",
                "runtime_state": "single_candidate_pending_scheduler_activation",
                "metric": "priority_runtime_candidate_count",
                "value": str(candidate_report.summary["priority_runtime_candidate_count"]),
            },
            {
                "runtime_component": "runtime_stub_replacement_lane",
                "runtime_state": "materialized_foundation_only",
                "metric": "lane_row_count",
                "value": str(scheduler_report.summary["lane_row_count"]),
            },
            {
                "runtime_component": "excluded_runtime_adapters",
                "runtime_state": "kept_outside_first_runtime_lane",
                "metric": "excluded_runtime_row_count",
                "value": str(candidate_report.summary["excluded_runtime_row_count"]),
            },
            {
                "runtime_component": "runtime_promotion_gate",
                "runtime_state": "closed",
                "metric": "unsatisfied_precondition_count",
                "value": str(precondition_report.summary["unsatisfied_count"]),
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "priority_runtime_candidate_count": candidate_report.summary["priority_runtime_candidate_count"],
            "lane_row_count": scheduler_report.summary["lane_row_count"],
            "excluded_runtime_row_count": candidate_report.summary["excluded_runtime_row_count"],
            "unsatisfied_precondition_count": precondition_report.summary["unsatisfied_count"],
            "promotable_now_count": candidate_report.summary["promotable_now_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_source_runtime_promotion_lane_now_at_single_candidate_scheduler_gate",
        }
        interpretation = [
            "Source-side no longer has a broad activation problem; it has one first runtime candidate lane, one materialized stub-replacement lane, and two excluded adapters.",
            "The remaining gate is scheduler/runtime promotion, not another round of host-level manual review.",
        ]
        return V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qi_a_share_source_runtime_promotion_lane_status_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
