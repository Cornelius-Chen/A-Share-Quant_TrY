from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134mi_a_share_execution_binding_refinement_audit_v1 import (
    V134MIAShareExecutionBindingRefinementAuditV1Analyzer,
)


@dataclass(slots=True)
class V134MJAShareMIExecutionBindingRefinementDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134MJAShareMIExecutionBindingRefinementDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134MJAShareMIExecutionBindingRefinementDirectionTriageV1Report:
        report = V134MIAShareExecutionBindingRefinementAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "blocker_count": report.summary["blocker_count"],
            "source_blocker_count": report.summary["source_blocker_count"],
            "authoritative_status": "execution_binding_kept_blocked_until_refined_source_and_replay_gates_close",
        }
        triage_rows = [
            {
                "component": "source_activation",
                "direction": "close_license_review_and_runtime_scheduler_gates_before_any_network-assisted_promotion",
            },
            {
                "component": "replay_and_governance",
                "direction": "retain_read_only_shadow_and_closed_execution_gates_until_binding_and_cost_model_backlogs_close",
            },
        ]
        interpretation = [
            "The blocker stack is now precise enough to guide closure work without reopening semantic research.",
            "Execution should remain blocked until the refined source gates and replay/governance blockers are explicitly resolved.",
        ]
        return V134MJAShareMIExecutionBindingRefinementDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MJAShareMIExecutionBindingRefinementDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MJAShareMIExecutionBindingRefinementDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mj_a_share_mi_execution_binding_refinement_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
