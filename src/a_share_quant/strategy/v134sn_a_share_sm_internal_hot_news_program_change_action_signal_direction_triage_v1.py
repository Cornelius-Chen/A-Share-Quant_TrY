from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134sm_a_share_internal_hot_news_program_change_action_signal_audit_v1 import (
    V134SMAShareInternalHotNewsProgramChangeActionSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V134SNAShareSMInternalHotNewsProgramChangeActionSignalDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134SNAShareSMInternalHotNewsProgramChangeActionSignalDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SNAShareSMInternalHotNewsProgramChangeActionSignalDirectionTriageV1Report:
        report = V134SMAShareInternalHotNewsProgramChangeActionSignalAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "top_risk_action_state": report.summary["top_risk_action_state"],
            "top_opportunity_action_state": report.summary["top_opportunity_action_state"],
            "global_program_action_mode_state": report.summary["global_program_action_mode_state"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "continue_serving_action-level_change_signal_above_action_surface",
        }
        triage_rows = [
            {
                "component": "stable_action_state",
                "direction": "treat_stable_as_no_new_program-level_reaction_needed_beyond_existing_action_surface",
            },
            {
                "component": "action_changed_state",
                "direction": "treat_action_changed_as_a_higher-priority_consumer_event_than_simple_snapshot_score_drift",
            },
            {
                "component": "signal_priority",
                "direction": "use_signal_priority_to_decide_whether_to_poll_only_or_raise_an_internal_alert",
            },
        ]
        interpretation = [
            "This is the narrowest program-facing signal in the hot-news pipeline so far.",
            "It should be used as an alert hint, while the action surface remains the explanatory layer.",
        ]
        return V134SNAShareSMInternalHotNewsProgramChangeActionSignalDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SNAShareSMInternalHotNewsProgramChangeActionSignalDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SNAShareSMInternalHotNewsProgramChangeActionSignalDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sn_a_share_sm_internal_hot_news_program_change_action_signal_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
