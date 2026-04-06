from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ui_a_share_internal_hot_news_program_runtime_stack_supervision_contract_audit_v1 import (
    V134UIAShareInternalHotNewsProgramRuntimeStackSupervisionContractAuditV1Analyzer,
)


@dataclass(slots=True)
class V134UJAShareUIInternalHotNewsProgramRuntimeStackSupervisionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134UJAShareUIInternalHotNewsProgramRuntimeStackSupervisionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UJAShareUIInternalHotNewsProgramRuntimeStackSupervisionDirectionTriageV1Report:
        report = V134UIAShareInternalHotNewsProgramRuntimeStackSupervisionContractAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "contract_row_count": report.summary["contract_row_count"],
            "supervision_loop_mode": report.summary["supervision_loop_mode"],
            "contract_action": report.summary["contract_action"],
            "sleep_strategy_seconds": report.summary["sleep_strategy_seconds"],
            "backoff_mode": report.summary["backoff_mode"],
            "authoritative_status": "continue_serving_runtime-stack_supervision_contract_as_the_topmost_supervising_instruction_row",
        }
        triage_rows = [
            {
                "component": "steady_supervision_branch",
                "direction": "keep_the_topmost supervising process on a steady supervision cadence when contract_action remains keep_steady_supervision",
            },
            {
                "component": "tight_supervision_branch",
                "direction": "tighten_the_topmost supervising cadence when contract_action rotates into tighten_supervision_loop or elevate_supervision_only",
            },
            {
                "component": "interrupt_supervision_branch",
                "direction": "interrupt_and reopen the requested target immediately when contract_action rotates into interrupt_supervision_loop_and_reopen_target",
            },
        ]
        interpretation = [
            "This is the topmost instruction row for the internal hot-news runtime stack.",
            "A supervising process can stop here and run the next cycle directly from the contract unless it needs deeper diagnostics.",
        ]
        return V134UJAShareUIInternalHotNewsProgramRuntimeStackSupervisionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UJAShareUIInternalHotNewsProgramRuntimeStackSupervisionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UJAShareUIInternalHotNewsProgramRuntimeStackSupervisionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134uj_a_share_ui_internal_hot_news_program_runtime_stack_supervision_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
