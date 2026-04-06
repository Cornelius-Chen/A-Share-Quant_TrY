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
class V134NQAShareRuntimeCandidateDependencyAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134NQAShareRuntimeCandidateDependencyAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.decision_surface_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_allowlist_decision_surface_v1.csv"
        )
        self.runtime_priority_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_runtime_priority_registry_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_runtime_candidate_dependency_status_v1.csv"
        )

    def analyze(self) -> V134NQAShareRuntimeCandidateDependencyAuditV1Report:
        decision_rows = _read_csv(self.decision_surface_path)
        runtime_rows = _read_csv(self.runtime_priority_path)

        pending_batch_one_count = sum(
            row["manual_license_decision"] == "pending" or row["manual_runtime_eligibility"] == "pending"
            for row in decision_rows
        )

        rows = []
        for row in runtime_rows:
            adapter_id = row["adapter_id"]
            if adapter_id == "network_html_article_fetch":
                if pending_batch_one_count == 0:
                    dependency_state = "manual_batch_one_cleared_pending_runtime_scheduler"
                    promotable_now = "False"
                    blocking_reason = "batch-one manual approvals complete; runtime scheduler gate still closed"
                else:
                    dependency_state = "blocked_by_batch_one_manual_pending"
                    promotable_now = "False"
                    blocking_reason = f"pending_batch_one_count = {pending_batch_one_count}"
            elif adapter_id == "network_social_column_fetch":
                dependency_state = "review_only_nonpromotive"
                promotable_now = "False"
                blocking_reason = "social column adapter remains review-only by design"
            else:
                dependency_state = "reserved_for_future_primary_sources"
                promotable_now = "False"
                blocking_reason = "official primary host inventory not yet activated"

            rows.append(
                {
                    "adapter_id": adapter_id,
                    "queue_priority": row["queue_priority"],
                    "dependency_state": dependency_state,
                    "promotable_now": promotable_now,
                    "blocking_reason": blocking_reason,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "runtime_row_count": len(rows),
            "promotable_now_count": sum(row["promotable_now"] == "True" for row in rows),
            "pending_batch_one_count": pending_batch_one_count,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_runtime_candidate_dependency_surface_reaudited_after_manual_batch_one_approval",
        }
        interpretation = [
            "Runtime promotion remains tied explicitly to batch-one decisions rather than to a vague scheduler gate.",
            "The first runtime candidate now clears manual review but remains blocked by runtime scheduler gating.",
        ]
        return V134NQAShareRuntimeCandidateDependencyAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NQAShareRuntimeCandidateDependencyAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NQAShareRuntimeCandidateDependencyAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nq_a_share_runtime_candidate_dependency_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
