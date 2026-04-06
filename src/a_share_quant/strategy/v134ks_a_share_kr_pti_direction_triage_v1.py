from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134kr_a_share_pti_foundation_audit_v1 import (
    V134KRASharePTIFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134KSAShareKRPTIDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KSAShareKRPTIDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134KSAShareKRPTIDirectionTriageV1Report:
        audit = V134KRASharePTIFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "pti_component": "event_ledger",
                "direction": "retain_as_current_point_in_time_source_of_truth_for_event_visibility",
            },
            {
                "pti_component": "time_slice_view",
                "direction": "retain_as_bootstrap_consumption_surface_for_replay_and_serving_workstreams",
            },
            {
                "pti_component": "state_transition_journal",
                "direction": "retain_bootstrap_visibility_and_attention_transitions_and_expand_into_board_reentry_execution_states_later",
            },
            {
                "pti_component": "next_frontier",
                "direction": "move_into_replay_workstream_using_bootstrap_pti_surfaces_as_input",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134ks_a_share_kr_pti_direction_triage_v1",
            "event_ledger_count": audit.summary["event_ledger_count"],
            "time_slice_count": audit.summary["time_slice_count"],
            "authoritative_status": "pti_workstream_complete_enough_to_freeze_as_bootstrap_and_shift_into_replay_population",
        }
        interpretation = [
            "V1.34KS converts the PTI audit into direction.",
            "The next correct move is replay: the PTI layer is now explicit enough that downstream shadow and serving layers can consume legal visibility surfaces rather than inventing them.",
        ]
        return V134KSAShareKRPTIDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KSAShareKRPTIDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KSAShareKRPTIDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ks_a_share_kr_pti_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
