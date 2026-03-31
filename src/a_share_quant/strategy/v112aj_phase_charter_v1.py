from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AJPhaseCharterReport:
    summary: dict[str, Any]
    charter: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "charter": self.charter,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AJPhaseCharterAnalyzer:
    def analyze(self, *, owner_review_payload: dict[str, Any]) -> V112AJPhaseCharterReport:
        owner_summary = dict(owner_review_payload.get("summary", {}))
        if not bool(owner_summary.get("enter_v112ai_waiting_state_now", True)) and not bool(
            owner_summary.get("ready_for_phase_check_next")
        ):
            raise ValueError("V1.12AJ requires the completed V1.12AI owner review.")

        charter = {
            "phase_name": "V1.12AJ CPO Bounded Label-Draft Dataset Assembly",
            "mission": (
                "Assemble the first bounded CPO label-draft dataset by combining truth-candidate rows with "
                "ready and guarded labels, while preserving support, overlay, and pending rows as context-only layers."
            ),
            "in_scope": [
                "assemble truth-candidate draft rows from primary and secondary surfaces",
                "attach ready and guarded labels only",
                "preserve support, overlay, and pending rows as explicit non-truth context",
                "keep review-only future labels and confirmed-only review labels out of draft truth",
            ],
            "out_of_scope": [
                "formal label freeze",
                "formal training",
                "formal signal generation",
                "promotion of context rows into truth rows",
            ],
            "success_criteria": [
                "draft-ready and guarded labels are assembled into a bounded dataset layer",
                "support, overlay, and pending objects remain explicit but outside truth-candidate rows",
                "review-only and confirmed-only labels do not leak into draft truth",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112aj_cpo_bounded_label_draft_dataset_assembly",
            "do_open_v112aj_now": True,
            "recommended_first_action": "freeze_v112aj_cpo_bounded_label_draft_dataset_assembly_v1",
        }
        interpretation = [
            "V1.12AJ is the first dataset-shaped assembly step, but it still sits fully below training rights.",
            "The core idea is truth-candidate rows plus context-only rows, not a fake-clean all-truth dataset.",
            "Only ready and guarded labels may enter the draft truth layer.",
        ]
        return V112AJPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112aj_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AJPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
