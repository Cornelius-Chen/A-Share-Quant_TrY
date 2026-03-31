from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ACPhaseClosureCheckReport:
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


class V112ACPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112ACPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112ac_as_review_only_unsupervised_challenge_success",
            "v112ac_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112ac_waiting_state_now": True,
            "allow_auto_role_replacement_now": False,
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ac_phase_check",
                "actual": {
                    "supportive_cluster_count": phase_summary.get("supportive_cluster_count"),
                    "challenging_cluster_count": phase_summary.get("challenging_cluster_count"),
                    "spillover_separation_supported": phase_summary.get("spillover_separation_supported"),
                    "pending_quiet_window_supported": phase_summary.get("pending_quiet_window_supported"),
                },
                "reading": "The unsupervised challenger returned usable review structure, but governance boundaries remain intact.",
            }
        ]
        interpretation = [
            "V1.12AC closes once the challenger output is frozen as review-only evidence.",
            "The next lawful move is owner review, not automatic replacement of the cohort map.",
        ]
        return V112ACPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ac_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ACPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
