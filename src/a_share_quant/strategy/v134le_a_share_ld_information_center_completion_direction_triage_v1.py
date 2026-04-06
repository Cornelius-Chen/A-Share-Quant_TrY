from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ld_a_share_information_center_foundation_completion_audit_v1 import (
    V134LDAShareInformationCenterFoundationCompletionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134LEAShareLDInformationCenterCompletionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134LEAShareLDInformationCenterCompletionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134LEAShareLDInformationCenterCompletionDirectionTriageV1Report:
        audit = V134LDAShareInformationCenterFoundationCompletionAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "completion_component": "foundation",
                "direction": "freeze_current_13_workstream_information_center_foundation_as_authoritative_base",
            },
            {
                "completion_component": "backlogs",
                "direction": "retain_as_named_backlogs_instead_of_faking_full_promotion",
            },
            {
                "completion_component": "future_frontier",
                "direction": "shift_later_into_source_activation_business_reference_purity_closure_board_state_derivation_and_live_like_opening",
            },
        ]
        summary = {
            "workstream_count": audit.summary["workstream_count"],
            "foundation_complete_count": audit.summary["foundation_complete_count"],
            "authoritative_status": "information_center_foundation_complete_enough_to_freeze_and_review",
        }
        interpretation = [
            "The information center is now complete enough at the foundation level to stop blind construction and start deliberate backlog closure or source activation by explicit frontier shifts.",
            "This is the correct macro stopline: the center exists, but its remaining growth should be controlled by named gaps rather than continuous undirected expansion.",
        ]
        return V134LEAShareLDInformationCenterCompletionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LEAShareLDInformationCenterCompletionDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LEAShareLDInformationCenterCompletionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134le_a_share_ld_information_center_completion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
