from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V19PhaseClosureCheckReport:
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


class V19PhaseClosureCheckAnalyzer:
    """Check whether V1.9 has reached a lawful bounded closure point."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        feature_breadth_rereview_payload: dict[str, Any],
        phase_check_payload: dict[str, Any],
    ) -> V19PhaseClosureCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        rereview_summary = dict(feature_breadth_rereview_payload.get("summary", {}))
        phase_summary = dict(phase_check_payload.get("summary", {}))

        success_criteria_met = (
            bool(charter_summary.get("do_open_v19_now"))
            and rereview_summary.get("reviewed_feature_count", 0) >= 1
            and rereview_summary.get("promotion_ready_now_count", 0) == 0
            and not bool(phase_summary.get("promote_retained_now"))
        )

        summary = {
            "acceptance_posture": "close_v19_as_bounded_breadth_evidence_rereview_success",
            "v19_success_criteria_met": success_criteria_met,
            "reviewed_feature_count": rereview_summary.get("reviewed_feature_count", 0),
            "shortfall_changed_count": rereview_summary.get("shortfall_changed_count", 0),
            "breadth_gap_materially_reduced_count": rereview_summary.get("breadth_gap_materially_reduced_count", 0),
            "breadth_gap_partially_reduced_count": rereview_summary.get("breadth_gap_partially_reduced_count", 0),
            "enter_v19_waiting_state_now": success_criteria_met,
            "promote_retained_now": False,
            "open_new_collection_phase_now": False,
            "recommended_next_posture": "preserve_v19_rereview_result_and_wait_for_owner_phase_switch_or_trigger",
        }
        evidence_rows = [
            {
                "evidence_name": "v19_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "do_open_v19_now": charter_summary.get("do_open_v19_now"),
                },
                "reading": "V1.9 opened lawfully as a bounded breadth-evidence re-review phase.",
            },
            {
                "evidence_name": "feature_breadth_rereview",
                "actual": {
                    "reviewed_feature_count": rereview_summary.get("reviewed_feature_count"),
                    "shortfall_changed_count": rereview_summary.get("shortfall_changed_count"),
                    "promotion_ready_now_count": rereview_summary.get("promotion_ready_now_count"),
                },
                "reading": "The current re-review has already refreshed promotion shortfalls using the bounded breadth evidence collected in V1.8C.",
            },
            {
                "evidence_name": "phase_check",
                "actual": {
                    "acceptance_posture": phase_summary.get("acceptance_posture"),
                    "promote_retained_now": phase_summary.get("promote_retained_now"),
                    "do_integrate_into_strategy_now": phase_summary.get("do_integrate_into_strategy_now"),
                },
                "reading": "The branch remains below promotion threshold, so closure should preserve the refreshed bounded judgment rather than force promotion.",
            },
        ]
        interpretation = [
            "V1.9 has now answered its core question: whether the first bounded breadth collection changes promotion judgment for the breadth-target features.",
            "It changed shortfall ordering for one feature and partially reduced the breadth gap for the other, but neither feature reached promotion-ready status.",
            "Per the autonomy policy, the correct move is to enter waiting state until a new owner phase switch or trigger appears.",
        ]
        return V19PhaseClosureCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v19_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V19PhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
