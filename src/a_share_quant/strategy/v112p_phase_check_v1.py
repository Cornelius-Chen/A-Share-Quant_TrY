from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112PPhaseCheckReport:
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


class V112PPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        registry_payload: dict[str, Any],
    ) -> V112PPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        registry_summary = dict(registry_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112p_as_registry_freeze_only",
            "do_open_v112p_now": charter_summary.get("do_open_v112p_now"),
            "selected_archetype": charter_summary.get("selected_archetype"),
            "cohort_row_count": registry_summary.get("cohort_row_count"),
            "source_count": registry_summary.get("source_count"),
            "remaining_gap_count": registry_summary.get("remaining_gap_count"),
            "ready_for_phase_closure_next": True,
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "recommended_next_posture": "close_v112p_and_discuss_missing_information_before_bounded_candidate_validation",
        }
        evidence_rows = [
            {
                "evidence_name": "full_cycle_registry",
                "actual": {
                    "information_layer_count": registry_summary.get("information_layer_count"),
                    "cohort_row_count": registry_summary.get("cohort_row_count"),
                    "source_count": registry_summary.get("source_count"),
                    "remaining_gap_count": registry_summary.get("remaining_gap_count"),
                },
                "reading": "The CPO line now has a broad multi-layer registry rather than only a narrow training pilot memory.",
            }
        ]
        interpretation = [
            "V1.12P succeeds once CPO full-cycle information is broad enough to support an owner discussion about missing information and validation order.",
            "This remains a review-memory and scope-management phase above training and feature promotion.",
        ]
        return V112PPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112p_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112PPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
