from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134no_a_share_batch_one_decision_closure_gate_audit_v1 import (
    V134NOAShareBatchOneDecisionClosureGateAuditV1Analyzer,
)


@dataclass(slots=True)
class V134NPAShareNOBatchOneClosureDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134NPAShareNOBatchOneClosureDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134NPAShareNOBatchOneClosureDirectionTriageV1Report:
        report = V134NOAShareBatchOneDecisionClosureGateAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "decision_unit_count": report.summary["decision_unit_count"],
            "pending_manual_unit_count": report.summary["pending_manual_unit_count"],
            "authoritative_status": "batch_one_closure_depends_on_manual_field_resolution_not_more_design",
        }
        triage_rows = [
            {
                "component": "primary_host_family",
                "direction": "resolve_primary_host_family_manual_fields_before_any_other_batch_one_closure",
            },
            {
                "component": "independent_hosts",
                "direction": "close_independent_hosts_only_after_primary_host_family_has_a_non_pending_outcome",
            },
            {
                "component": "sibling_host",
                "direction": "retain_sibling_host_as_last_closure_step_after_primary_host_family_outcome",
            },
            {
                "component": "promotion_gate",
                "direction": "keep_allowlist_promotion_closed_until_manual_license_and_runtime_fields_stop_being_pending",
            },
        ]
        interpretation = [
            "The next source-side gain now depends on closing manual fields, not on extending the queue framework.",
            "This is a closure-order problem, not a discovery problem.",
        ]
        return V134NPAShareNOBatchOneClosureDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NPAShareNOBatchOneClosureDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NPAShareNOBatchOneClosureDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134np_a_share_no_batch_one_closure_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
