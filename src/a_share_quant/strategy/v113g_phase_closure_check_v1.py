from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113GPhaseClosureCheckReport:
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


class V113GPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V113GPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v113g_as_commercial_space_deep_study_scope_success",
            "v113g_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "selected_archetype": phase_summary.get("selected_archetype"),
            "enter_v113g_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_label_freeze_now": False,
            "recommended_next_posture": "decide_between_bounded_candidate_validation_and_bounded_review_sheet_widening",
        }
        evidence_rows = [
            {
                "evidence_name": "v113g_phase_check",
                "actual": {
                    "validated_local_seed_count": phase_summary.get("validated_local_seed_count"),
                    "owner_named_candidate_count": phase_summary.get("owner_named_candidate_count"),
                },
                "reading": "The deep-study registry now distinguishes clean local seeds from wider owner-named candidates.",
            }
        ]
        interpretation = [
            "V1.13G closes once commercial-space is frozen as a high-value deep-study archetype rather than a narrow object-correction problem.",
            "The line remains above downstream pilot widening and training until a later bounded validation move is chosen.",
        ]
        return V113GPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113g_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113GPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
