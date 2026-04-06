from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134nm_a_share_batch_one_allowlist_decision_surface_audit_v1 import (
    V134NMAShareBatchOneAllowlistDecisionSurfaceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134NNAShareNMBatchOneDecisionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134NNAShareNMBatchOneDecisionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134NNAShareNMBatchOneDecisionDirectionTriageV1Report:
        report = V134NMAShareBatchOneAllowlistDecisionSurfaceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "decision_unit_count": report.summary["decision_unit_count"],
            "pending_manual_decision_count": report.summary["pending_manual_decision_count"],
            "authoritative_status": "batch_one_allowlist_decision_surface_ready_for_manual_review_but_closed",
        }
        triage_rows = [
            {
                "component": "manual_decision_fields",
                "direction": "retain_explicit_license_and_runtime_fields_for_all_batch_one_hosts",
            },
            {
                "component": "decision_order",
                "direction": "review_primary_sina_host_first_then_independent_hosts_then_sibling_host",
            },
            {
                "component": "promotion_gate",
                "direction": "keep_promotion_closed_until_manual_decision_fields_change_from_pending",
            },
        ]
        interpretation = [
            "Batch-one can now be reviewed reproducibly without reopening queue design.",
            "The next gain comes only from manual decisions being filled, not from further reshaping the same surface.",
        ]
        return V134NNAShareNMBatchOneDecisionDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NNAShareNMBatchOneDecisionDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NNAShareNMBatchOneDecisionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nn_a_share_nm_batch_one_decision_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
