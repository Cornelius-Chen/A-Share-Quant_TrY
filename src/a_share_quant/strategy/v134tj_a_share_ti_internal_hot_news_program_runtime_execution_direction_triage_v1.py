from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ti_a_share_internal_hot_news_program_runtime_execution_contract_audit_v1 import (
    V134TIAShareInternalHotNewsProgramRuntimeExecutionContractAuditV1Analyzer,
)


@dataclass(slots=True)
class V134TJAShareTIInternalHotNewsProgramRuntimeExecutionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134TJAShareTIInternalHotNewsProgramRuntimeExecutionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TJAShareTIInternalHotNewsProgramRuntimeExecutionDirectionTriageV1Report:
        report = V134TIAShareInternalHotNewsProgramRuntimeExecutionContractAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "contract_row_count": report.summary["contract_row_count"],
            "runtime_consumer_mode": report.summary["runtime_consumer_mode"],
            "contract_action": report.summary["contract_action"],
            "sleep_strategy_seconds": report.summary["sleep_strategy_seconds"],
            "backoff_mode": report.summary["backoff_mode"],
            "authoritative_status": "continue_serving_runtime-execution_contract_above_the_runtime-envelope",
        }
        triage_rows = [
            {
                "component": "passive_execution_branch",
                "direction": "keep_the_loop_on_sleep-and-poll_when_contract_action_stays_keep_passive_polling",
            },
            {
                "component": "elevated_execution_branch",
                "direction": "tighten_the_loop_and_reopen_requested_layers_when_contract_action_rotates_into_elevate_or_reopen states",
            },
            {
                "component": "interrupt_execution_branch",
                "direction": "break_the_current_loop_and_reassess_immediately_when_contract_action_rotates_into_interrupt_loop_and_reopen_target",
            },
        ]
        interpretation = [
            "This is the highest execution-facing contract in the internal hot-news stack.",
            "A consumer loop can use it as the next-iteration instruction without reading any lower diagnostic tables.",
        ]
        return V134TJAShareTIInternalHotNewsProgramRuntimeExecutionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TJAShareTIInternalHotNewsProgramRuntimeExecutionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TJAShareTIInternalHotNewsProgramRuntimeExecutionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134tj_a_share_ti_internal_hot_news_program_runtime_execution_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
