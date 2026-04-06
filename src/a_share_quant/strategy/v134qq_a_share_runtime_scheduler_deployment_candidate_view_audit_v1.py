from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134QQAShareRuntimeSchedulerDeploymentCandidateViewAuditV1Report:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


class V134QQAShareRuntimeSchedulerDeploymentCandidateViewAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.stub_lane_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_runtime_scheduler_stub_replacement_lane_v1.csv"
        )
        self.scheduler_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_scheduler_runtime_registry_v1.csv"
        )
        self.runtime_queue_path = (
            repo_root
            / "data"
            / "temp"
            / "info_center"
            / "review_queue"
            / "a_share_network_runtime_deployment_queue_v1.csv"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_runtime_scheduler_deployment_candidate_view_v1.csv"
        )

    def analyze(self) -> V134QQAShareRuntimeSchedulerDeploymentCandidateViewAuditV1Report:
        stub_lane_rows = _read_csv(self.stub_lane_path)
        scheduler_rows = _read_csv(self.scheduler_registry_path)
        queue_rows = _read_csv(self.runtime_queue_path)
        scheduler_by_adapter = {row["adapter_id"]: row for row in scheduler_rows}
        queue_by_adapter = {row["adapter_id"]: row for row in queue_rows}

        candidate_rows: list[dict[str, Any]] = []
        for row in stub_lane_rows:
            adapter_id = row["adapter_id"]
            scheduler = scheduler_by_adapter[adapter_id]
            queue = queue_by_adapter[adapter_id]
            candidate_rows.append(
                {
                    "adapter_id": adapter_id,
                    "flow_id": scheduler["flow_id"],
                    "retry_policy_id": scheduler["retry_policy_id"],
                    "activation_scope": scheduler["activation_scope"],
                    "queue_state": queue["queue_state"],
                    "lane_state": row["lane_state"],
                    "deployment_candidate_state": "single_candidate_pending_governance_and_scheduler_opening",
                    "promotable_now": "False",
                    "blocking_reason": row["blocking_reason"],
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(candidate_rows[0].keys()))
            writer.writeheader()
            writer.writerows(candidate_rows)

        summary = {
            "candidate_row_count": len(candidate_rows),
            "promotable_now_count": sum(row["promotable_now"] == "True" for row in candidate_rows),
            "artifact_path": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_runtime_scheduler_deployment_candidate_view_materialized",
        }
        interpretation = [
            "Source-side runtime followthrough now has a concrete single-row deployment candidate view instead of only separate queue and lane surfaces.",
            "The candidate remains non-promotive because scheduler activation and governance gates are still closed.",
        ]
        return V134QQAShareRuntimeSchedulerDeploymentCandidateViewAuditV1Report(
            summary=summary, candidate_rows=candidate_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134QQAShareRuntimeSchedulerDeploymentCandidateViewAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QQAShareRuntimeSchedulerDeploymentCandidateViewAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qq_a_share_runtime_scheduler_deployment_candidate_view_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
