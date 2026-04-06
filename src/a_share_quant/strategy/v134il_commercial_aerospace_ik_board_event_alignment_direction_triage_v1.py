from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ik_commercial_aerospace_board_event_alignment_supervision_audit_v1 import (
    V134IKCommercialAerospaceBoardEventAlignmentSupervisionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ILCommercialAerospaceIKBoardEventAlignmentDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134ILCommercialAerospaceIKBoardEventAlignmentDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ILCommercialAerospaceIKBoardEventAlignmentDirectionTriageV1Report:
        audit = V134IKCommercialAerospaceBoardEventAlignmentSupervisionAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "alignment_label": "aligned_board_supportive_response",
                "direction": "retain_as_the_cleanest_positive_alignment_case",
            },
            {
                "alignment_label": "turning_point_overheat_alignment",
                "direction": "retain_as_negative_turning_point_alignment_not_supportive_response",
            },
            {
                "alignment_label": "pre_turn_alignment_watch",
                "direction": "retain_as_watch_not_confirmation",
            },
            {
                "alignment_label": "lockout_misaligned_board_response",
                "direction": "retain_as_negative_alignment_case",
            },
            {
                "alignment_label": "raw_only_post_lockout_alignment_absent",
                "direction": "retain_as_explicit_absence_not_as_unknown_to_be_guessed",
            },
            {
                "alignment_label": "capital_true_selection",
                "direction": "continue_blocked_even_after_alignment_layer_exists",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134il_commercial_aerospace_ik_board_event_alignment_direction_triage_v1",
            "event_seed_count": audit.summary["event_seed_count"],
            "authoritative_status": "retain_board_event_alignment_as_a_new_supervision_layer_without_pretending_it_solves_true_selection",
        }
        interpretation = [
            "V1.34IL converts board-event alignment into direction.",
            "The alignment layer closes one named gap, but it still does not collapse the remaining gaps into a true-selection license.",
        ]
        return V134ILCommercialAerospaceIKBoardEventAlignmentDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ILCommercialAerospaceIKBoardEventAlignmentDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ILCommercialAerospaceIKBoardEventAlignmentDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134il_commercial_aerospace_ik_board_event_alignment_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
