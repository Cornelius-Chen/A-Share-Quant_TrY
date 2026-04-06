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
class V134NOAShareBatchOneDecisionClosureGateAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134NOAShareBatchOneDecisionClosureGateAuditV1Analyzer:
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
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_batch_one_decision_closure_gate_status_v1.csv"
        )

    def analyze(self) -> V134NOAShareBatchOneDecisionClosureGateAuditV1Report:
        decision_rows = _read_csv(self.decision_surface_path)

        primary_rows = [row for row in decision_rows if row["review_priority_order"] == "1"]
        independent_rows = [row for row in decision_rows if row["review_priority_order"] == "2"]
        sibling_rows = [row for row in decision_rows if row["review_priority_order"] == "3"]

        pending_rows = [
            row
            for row in decision_rows
            if row["manual_license_decision"] == "pending" or row["manual_runtime_eligibility"] == "pending"
        ]

        rows = [
            {
                "closure_component": "primary_host_family",
                "closure_state": "manual_decision_completed",
                "supporting_count": len(primary_rows),
                "blocking_reason": "primary batch-one host family manual approval is complete",
            },
            {
                "closure_component": "independent_hosts",
                "closure_state": "manual_decision_completed_after_primary",
                "supporting_count": len(independent_rows),
                "blocking_reason": "independent T2 host manual approvals are complete",
            },
            {
                "closure_component": "sibling_host_dependency",
                "closure_state": "manual_decision_completed_after_primary_outcome",
                "supporting_count": len(sibling_rows),
                "blocking_reason": "sibling Sina host manual approval is complete after the primary family outcome",
            },
            {
                "closure_component": "promotion_gate",
                "closure_state": "closed_pending_runtime_promotion",
                "supporting_count": len(pending_rows),
                "blocking_reason": "manual approvals are complete but runtime promotion remains closed",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "decision_unit_count": len(decision_rows),
            "pending_manual_unit_count": len(pending_rows),
            "manual_decision_completed_count": len(decision_rows) - len(pending_rows),
            "primary_host_family_count": len(primary_rows),
            "independent_host_count": len(independent_rows),
            "sibling_host_count": len(sibling_rows),
            "promotable_now_count": 0,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_batch_one_decision_closure_completed_but_runtime_promotion_kept_closed",
        }
        interpretation = [
            "Batch-one closure gate now shows that manual review is complete instead of pending.",
            "The remaining block is runtime promotion, not another host-level decision step.",
        ]
        return V134NOAShareBatchOneDecisionClosureGateAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NOAShareBatchOneDecisionClosureGateAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NOAShareBatchOneDecisionClosureGateAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134no_a_share_batch_one_decision_closure_gate_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
