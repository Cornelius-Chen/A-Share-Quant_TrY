from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AIPhaseClosureCheckReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AIPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112AIPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112ai_as_label_draft_integrity_owner_review_success",
            "v112ai_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112ai_waiting_state_now": True,
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ai_phase_check",
                "actual": {
                    "draft_ready_label_count": phase_summary.get("draft_ready_label_count"),
                    "guarded_draft_label_count": phase_summary.get("guarded_draft_label_count"),
                    "review_only_future_target_count": phase_summary.get("review_only_future_target_count"),
                    "confirmed_only_review_label_count": phase_summary.get("confirmed_only_review_label_count"),
                    "dropped_label_count": phase_summary.get("dropped_label_count"),
                },
                "reading": "The label draft is now owner-tiered into ready, guarded, review-only, and confirmed-only classes without any silent deletion.",
            }
        ]
        interpretation = [
            "V1.12AI closes once the bounded draft has an explicit owner disposition map.",
            "The next lawful move is bounded label-draft dataset assembly using only ready and guarded labels.",
        ]
        return V112AIPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ai_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AIPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
