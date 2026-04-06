from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134lw_a_share_execution_binding_blocker_stack_audit_v1 import (
    V134LWAShareExecutionBindingBlockerStackAuditV1Analyzer,
)


@dataclass(slots=True)
class V134LXAShareLWExecutionBindingDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134LXAShareLWExecutionBindingDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134LXAShareLWExecutionBindingDirectionTriageV1Report:
        audit = V134LWAShareExecutionBindingBlockerStackAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "execution_binding",
                "direction": "keep_blocked",
            },
            {
                "component": "next_frontier",
                "direction": "close_network_fetch_binding_and_replay_execution_cost_model_backlogs_before_reopening_execution_authority",
            },
        ]
        summary = {
            "blocker_count": audit.summary["blocker_count"],
            "governance_blocker_count": audit.summary["governance_blocker_count"],
            "replay_blocker_count": audit.summary["replay_blocker_count"],
            "authoritative_status": "execution_binding_still_blocked_by_named_stack",
        }
        interpretation = [
            "Execution authority should remain closed because the blocker stack is now explicit and still active.",
            "The next useful work is not another promotion discussion; it is closing the named infrastructure blockers in order.",
        ]
        return V134LXAShareLWExecutionBindingDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LXAShareLWExecutionBindingDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LXAShareLWExecutionBindingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lx_a_share_lw_execution_binding_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
