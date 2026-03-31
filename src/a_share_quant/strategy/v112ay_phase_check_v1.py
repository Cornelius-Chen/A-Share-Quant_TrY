from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AYPhaseCheckReport:
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


class V112AYPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        training_layer_review_payload: dict[str, Any],
    ) -> V112AYPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(training_layer_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112ay_as_guarded_branch_training_layer_review",
            "do_open_v112ay_now": charter_summary.get("do_open_v112ay_now"),
            "guarded_training_layer_admissible_count": review_summary.get("guarded_training_layer_admissible_count"),
            "branch_rows_retained_review_only_count": review_summary.get("branch_rows_retained_review_only_count"),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": review_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ay_branch_training_layer_review",
                "actual": {
                    "guarded_training_layer_admissible_count": review_summary.get("guarded_training_layer_admissible_count"),
                    "branch_rows_retained_review_only_count": review_summary.get("branch_rows_retained_review_only_count"),
                    "core_targets_stable_after_guarded_branch_admission": review_summary.get("core_targets_stable_after_guarded_branch_admission"),
                },
                "reading": "The review is only successful if the project can cut admissible guarded branch rows away from still-mixed branch rows.",
            }
        ]
        interpretation = [
            "V1.12AY is a bounded training-layer review, not formal training.",
            "Formal training and signal rights remain closed.",
        ]
        return V112AYPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ay_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AYPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
