from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134mu_a_share_execution_binding_blocker_stack_reaudit_v1 import (
    V134MUAShareExecutionBindingBlockerStackReauditV1Analyzer,
)


@dataclass(slots=True)
class V134MVAShareMUExecutionBindingReauditDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134MVAShareMUExecutionBindingReauditDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134MVAShareMUExecutionBindingReauditDirectionTriageV1Report:
        report = V134MUAShareExecutionBindingBlockerStackReauditV1Analyzer(self.repo_root).analyze()
        summary = {
            "blocker_count": report.summary["blocker_count"],
            "replay_blocker_count": report.summary["replay_blocker_count"],
            "authoritative_status": "execution_binding_kept_blocked_until_source_gates_and_replay_boundary_residuals_close",
        }
        triage_rows = [
            {
                "component": "source_activation",
                "direction": "process_allowlist_and_runtime_queues_before_any_network-assisted_live_like_shift",
            },
            {
                "component": "replay",
                "direction": "close_boundary_and_calendar_residuals_and_replace_execution_stub_before_any_binding_promotion",
            },
        ]
        interpretation = [
            "The blocker stack is now concrete enough to separate source-side queue processing from replay-side coverage closure.",
            "That is the correct stopline before any future live_like or execution promotion review.",
        ]
        return V134MVAShareMUExecutionBindingReauditDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MVAShareMUExecutionBindingReauditDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MVAShareMUExecutionBindingReauditDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mv_a_share_mu_execution_binding_reaudit_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
