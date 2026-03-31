from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112NPhaseClosureCheckReport:
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


class V112NPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112NPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112n_as_shadow_rerun_complete",
            "v112n_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112n_waiting_state_now": True,
            "allow_auto_feature_promotion_now": False,
            "allow_auto_label_action_now": False,
            "recommended_next_posture": "preserve_inner_draft_as_descriptive_review_asset_until_new evidence if no incremental gain",
        }
        evidence_rows = [
            {
                "evidence_name": "v112n_phase_check",
                "actual": {
                    "baseline_shadow_incremental_gain_present": phase_summary.get("baseline_shadow_incremental_gain_present"),
                    "gbdt_shadow_incremental_gain_present": phase_summary.get("gbdt_shadow_incremental_gain_present"),
                    "net_incremental_gain_present": phase_summary.get("net_incremental_gain_present"),
                },
                "reading": "V1.12N closes once the review-only shadow rerun establishes whether the inner-draft features add predictive value or remain descriptive only.",
            }
        ]
        interpretation = [
            "V1.12N is still review-only and cannot authorize feature promotion or label change.",
            "A no-gain result is still useful because it prevents over-reading the inner draft.",
        ]
        return V112NPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112n_phase_closure_check_report(
    *, reports_dir: Path, report_name: str, result: V112NPhaseClosureCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
