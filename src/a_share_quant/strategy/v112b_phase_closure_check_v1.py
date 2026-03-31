from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BPhaseClosureCheckReport:
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


class V112BPhaseClosureCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_check_payload: dict[str, Any],
    ) -> V112BPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112b_as_first_trainable_dataset_and_report_only_baseline_success",
            "v112b_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112b_waiting_state_now": True,
            "allow_auto_training_now": False,
            "recommended_next_posture": "preserve_v112b_baseline_for_owner_review_before_any_new_training_phase",
        }
        evidence_rows = [
            {
                "evidence_name": "v112b_phase_check",
                "actual": {
                    "dataset_frozen": bool(phase_summary.get("dataset_frozen")),
                    "baseline_readout_present": bool(phase_summary.get("baseline_readout_present")),
                    "allow_strategy_training_now": bool(phase_summary.get("allow_strategy_training_now")),
                },
                "reading": "V1.12B satisfies its mission once the first trainable dataset and report-only baseline both exist, while strategy training remains blocked.",
            }
        ]
        interpretation = [
            "V1.12B closes successfully after the first owner-accepted pilot dataset is frozen and the first baseline readout is produced.",
            "That is enough to stop without opening deployment, black-box work, or object widening.",
            "The correct next posture is waiting state until the owner reviews the baseline output and decides the next experiment.",
        ]
        return V112BPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112b_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
