from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qg_a_share_runtime_promotion_candidate_surface_audit_v1 import (
    V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer,
)
from a_share_quant.strategy.v134qo_a_share_runtime_scheduler_stub_replacement_lane_audit_v1 import (
    V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Analyzer,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.scheduler_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_scheduler_runtime_registry_v1.csv"
        )
        self.activation_policy_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_fetch_activation_policy_v1.csv"
        )
        self.retry_policy_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_fetch_retry_policy_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_runtime_scheduler_activation_precondition_status_v1.csv"
        )

    def analyze(self) -> V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Report:
        candidate_report = V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer(self.repo_root).analyze()
        lane_report = V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Analyzer(self.repo_root).analyze()
        scheduler_rows = _read_csv(self.scheduler_registry_path)
        activation_rows = _read_csv(self.activation_policy_path)
        retry_rows = _read_csv(self.retry_policy_path)

        html_candidate = next(row for row in candidate_report.rows if row["adapter_id"] == "network_html_article_fetch")
        html_scheduler = next(row for row in scheduler_rows if row["adapter_id"] == "network_html_article_fetch")
        html_activation = next(row for row in activation_rows if row["adapter_id"] == "network_html_article_fetch")
        retry_bound = any(row["retry_policy_id"] == html_scheduler["retry_policy_id"] for row in retry_rows)

        rows = [
            {
                "precondition": "single_runtime_candidate_isolated",
                "precondition_state": "satisfied",
                "supporting_count": candidate_report.summary["priority_runtime_candidate_count"],
                "blocking_reason": "single html-article runtime candidate has been isolated",
            },
            {
                "precondition": "activation_policy_bound",
                "precondition_state": "satisfied",
                "supporting_count": 1 if html_activation["activation_state"] == "policy_bound_not_activated" else 0,
                "blocking_reason": "html-article adapter already has selective-after-license-review activation policy",
            },
            {
                "precondition": "retry_policy_bound",
                "precondition_state": "satisfied" if retry_bound else "unsatisfied",
                "supporting_count": 1 if retry_bound else 0,
                "blocking_reason": (
                    "html-article adapter already has retry policy binding"
                    if retry_bound
                    else "retry policy binding missing for html-article adapter"
                ),
            },
            {
                "precondition": "scheduler_runtime_activation",
                "precondition_state": "unsatisfied",
                "supporting_count": 1 if html_scheduler["runtime_binding_state"] == "scheduler_stub_not_activated" else 0,
                "blocking_reason": "runtime binding still remains scheduler_stub_not_activated",
            },
            {
                "precondition": "scheduler_stub_replacement_lane_materialized",
                "precondition_state": "satisfied_foundation_only",
                "supporting_count": lane_report.summary["lane_row_count"],
                "blocking_reason": "single html-article scheduler stub replacement lane has been materialized",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "precondition_count": len(rows),
            "unsatisfied_count": sum(row["precondition_state"] == "unsatisfied" for row in rows),
            "priority_runtime_candidate_count": candidate_report.summary["priority_runtime_candidate_count"],
            "lane_row_count": lane_report.summary["lane_row_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_runtime_scheduler_activation_preconditions_materialized",
        }
        interpretation = [
            "The first runtime lane is no longer blocked by candidate ambiguity; it is narrowed to one scheduler activation precondition.",
            "The remaining source-side runtime blocker is scheduler stub activation, not host review or retry-policy design.",
            "A single scheduler-stub replacement lane is now explicitly materialized as foundation-ready support for that future activation step.",
        ]
        return V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qk_a_share_runtime_scheduler_activation_precondition_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
