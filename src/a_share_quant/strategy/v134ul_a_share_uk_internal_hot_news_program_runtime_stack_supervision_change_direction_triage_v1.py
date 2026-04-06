from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134uk_a_share_internal_hot_news_program_runtime_stack_supervision_contract_change_signal_audit_v1 import (
    V134UKAShareInternalHotNewsProgramRuntimeStackSupervisionContractChangeSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ULAShareUKInternalHotNewsProgramRuntimeStackSupervisionChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ULAShareUKInternalHotNewsProgramRuntimeStackSupervisionChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ULAShareUKInternalHotNewsProgramRuntimeStackSupervisionChangeDirectionTriageV1Report:
        report = V134UKAShareInternalHotNewsProgramRuntimeStackSupervisionContractChangeSignalAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "supervisor_mode_change": report.summary["supervisor_mode_change"],
            "supervision_loop_mode_change": report.summary["supervision_loop_mode_change"],
            "contract_action_change": report.summary["contract_action_change"],
            "sleep_strategy_change": report.summary["sleep_strategy_change"],
            "backoff_mode_change": report.summary["backoff_mode_change"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "continue_serving_runtime-stack_supervision_contract_change_signal_above_the_topmost_supervision_contract",
        }
        triage_rows = [
            {
                "component": "stable_supervision_contract_branch",
                "direction": "keep_the_current_topmost supervision configuration when the supervision-contract change signal remains stable",
            },
            {
                "component": "supervision_behavior_change_branch",
                "direction": "reconfigure_the_next supervising cycle when supervisor_mode_change, supervision_loop_mode_change, or contract_action_change flips state",
            },
            {
                "component": "cadence_change_branch",
                "direction": "update_topmost sleep and backoff behavior immediately when sleep_strategy_change or backoff_mode_change flips state",
            },
        ]
        interpretation = [
            "This is the topmost change detector for the runtime-stack supervision contract.",
            "A supervising process can watch it to know when actual topmost supervision behavior changed without rereading the full contract every cycle.",
        ]
        return V134ULAShareUKInternalHotNewsProgramRuntimeStackSupervisionChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ULAShareUKInternalHotNewsProgramRuntimeStackSupervisionChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ULAShareUKInternalHotNewsProgramRuntimeStackSupervisionChangeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ul_a_share_uk_internal_hot_news_program_runtime_stack_supervision_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
