from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_runtime_stack_supervision_contract_v1 import (
    MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisionContractV1,
)


@dataclass(slots=True)
class V134UIAShareInternalHotNewsProgramRuntimeStackSupervisionContractAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134UIAShareInternalHotNewsProgramRuntimeStackSupervisionContractAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UIAShareInternalHotNewsProgramRuntimeStackSupervisionContractAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisionContractV1(self.repo_root).materialize()
        rows = [
            {
                "component": "runtime_stack_supervision_contract",
                "component_state": "read_ready_internal_only",
                "metric": "contract_row_count",
                "value": str(materialized.summary["contract_row_count"]),
            },
            {
                "component": "supervision_loop_mode",
                "component_state": "materialized",
                "metric": "supervision_loop_mode",
                "value": materialized.summary["supervision_loop_mode"],
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
            "This is the topmost supervision contract above the compact supervisor surface and supervisor-loop signal layers.",
            "A supervising process can use it as the single-row instruction for its next cycle without rereading lower runtime-stack layers.",
        ]
        return V134UIAShareInternalHotNewsProgramRuntimeStackSupervisionContractAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UIAShareInternalHotNewsProgramRuntimeStackSupervisionContractAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UIAShareInternalHotNewsProgramRuntimeStackSupervisionContractAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ui_a_share_internal_hot_news_program_runtime_stack_supervision_contract_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
