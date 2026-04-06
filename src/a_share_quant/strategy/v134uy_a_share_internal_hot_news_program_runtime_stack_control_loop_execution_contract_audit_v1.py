from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_runtime_stack_control_loop_execution_contract_v1 import (
    MaterializeAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractV1,
)


@dataclass(slots=True)
class V134UYAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134UYAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UYAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractV1(self.repo_root).materialize()
        rows = [
            {
                "component": "runtime_stack_execution_contract",
                "component_state": "read_ready_internal_only",
                "metric": "contract_row_count",
                "value": str(materialized.summary["contract_row_count"]),
            },
            {
                "component": "runtime_consumer_mode",
                "component_state": "materialized",
                "metric": "runtime_consumer_mode",
                "value": materialized.summary["runtime_consumer_mode"],
            },
            {
                "component": "contract_action",
                "component_state": "materialized",
                "metric": "contract_action",
                "value": materialized.summary["contract_action"],
            },
            {
                "component": "sleep_strategy_seconds",
                "component_state": "materialized",
                "metric": "sleep_strategy_seconds",
                "value": materialized.summary["sleep_strategy_seconds"],
            },
        ]
        interpretation = [
            "This is the execution-facing contract above the runtime-stack control-loop runtime envelope.",
            "An outer controller can use it as the single-row instruction for its next cycle without rereading lower runtime-stack layers.",
        ]
        return V134UYAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UYAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UYAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134uy_a_share_internal_hot_news_program_runtime_stack_control_loop_execution_contract_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
