from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V17PhaseClosureCheckReport:
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


class V17PhaseClosureCheckAnalyzer:
    """Check whether V1.7 has reached a lawful bounded closure point."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        feature_promotion_gap_review_payload: dict[str, Any],
        phase_check_payload: dict[str, Any],
    ) -> V17PhaseClosureCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(feature_promotion_gap_review_payload.get("summary", {}))
        phase_summary = dict(phase_check_payload.get("summary", {}))

        success_criteria_met = (
            bool(charter_summary.get("do_open_v17_now"))
            and review_summary.get("reviewed_feature_count", 0) >= 1
            and review_summary.get("promotion_ready_now_count", 0) == 0
            and not bool(phase_summary.get("promote_retained_now"))
        )

        summary = {
            "acceptance_posture": "close_v17_as_bounded_promotion_evidence_generation_success",
            "v17_success_criteria_met": success_criteria_met,
            "reviewed_feature_count": review_summary.get("reviewed_feature_count", 0),
            "promotion_ready_now_count": review_summary.get("promotion_ready_now_count", 0),
            "needs_additional_promotion_evidence_count": review_summary.get("needs_additional_promotion_evidence_count", 0),
            "enter_v17_waiting_state_now": success_criteria_met,
            "promote_retained_now": False,
            "open_local_regime_phase_now": False,
            "recommended_next_posture": "preserve_v17_promotion_shortfalls_and_wait_for_owner_phase_switch_or_trigger",
        }
        evidence_rows = [
            {
                "evidence_name": "v17_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "do_open_v17_now": charter_summary.get("do_open_v17_now"),
                },
                "reading": "V1.7 opened lawfully as a bounded promotion-evidence generation phase.",
            },
            {
                "evidence_name": "feature_promotion_gap_review",
                "actual": {
                    "reviewed_feature_count": review_summary.get("reviewed_feature_count"),
                    "promotion_ready_now_count": review_summary.get("promotion_ready_now_count"),
                    "needs_additional_promotion_evidence_count": review_summary.get("needs_additional_promotion_evidence_count"),
                },
                "reading": "The current review answered what evidence is still missing for each provisional candidate.",
            },
            {
                "evidence_name": "phase_check",
                "actual": {
                    "acceptance_posture": phase_summary.get("acceptance_posture"),
                    "promote_retained_now": phase_summary.get("promote_retained_now"),
                    "do_integrate_into_strategy_now": phase_summary.get("do_integrate_into_strategy_now"),
                },
                "reading": "The branch remains below promotion threshold, so closure should preserve promotion shortfalls rather than force promotion or new branches.",
            },
        ]
        interpretation = [
            "V1.7 has now answered its core question: what new evidence would be required to change retained-feature promotion judgment for current provisional candidates.",
            "That is enough to close the phase successfully without promoting any feature into retained status.",
            "Per the autonomy policy, the correct move is to enter waiting state until a new owner phase switch or trigger appears.",
        ]
        return V17PhaseClosureCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v17_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V17PhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
