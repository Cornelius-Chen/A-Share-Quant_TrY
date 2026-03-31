from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12WaitingStateSummaryReport:
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


class V12WaitingStateSummaryAnalyzer:
    """Summarize when V1.2 should enter explicit waiting instead of forcing a new branch."""

    def analyze(
        self,
        *,
        bottleneck_check_payload: dict[str, Any],
        v6_first_lane_phase_check_payload: dict[str, Any],
        v6_reassessment_payload: dict[str, Any],
    ) -> V12WaitingStateSummaryReport:
        bottleneck_summary = dict(bottleneck_check_payload.get("summary", {}))
        first_lane_phase_summary = dict(v6_first_lane_phase_check_payload.get("summary", {}))
        v6_reassessment_summary = dict(v6_reassessment_payload.get("summary", {}))

        primary_bottleneck_still_carry = (
            str(bottleneck_summary.get("acceptance_posture", ""))
            == "keep_v12_primary_bottleneck_as_carry_row_diversity_gap"
        )
        first_review_unchanged = not bool(first_lane_phase_summary.get("do_open_second_v6_lane_now"))
        second_review_unchanged = not bool(v6_reassessment_summary.get("do_open_second_v6_lane_now"))
        no_local_next_step = first_review_unchanged and second_review_unchanged
        enter_waiting_state = (
            primary_bottleneck_still_carry
            and no_local_next_step
            and not bool(v6_reassessment_summary.get("do_prepare_next_refresh_now"))
        )

        summary = {
            "acceptance_posture": (
                "enter_v12_explicit_waiting_state_after_v6_local_hold"
                if enter_waiting_state
                else "hold_v12_waiting_state_summary_until_local_actions_exhaust"
            ),
            "primary_bottleneck_still_carry_row_diversity": primary_bottleneck_still_carry,
            "v6_local_next_step_available": not no_local_next_step,
            "repeated_phase_review_no_change": first_review_unchanged and second_review_unchanged,
            "do_open_v7_now": False,
            "do_reopen_existing_substrate_now": False,
            "enter_explicit_waiting_state_now": enter_waiting_state,
            "recommended_next_posture": (
                "explicit_waiting_state_until_new_trigger_or_owner_phase_switch"
                if enter_waiting_state
                else "continue_current_phase_checks"
            ),
        }
        evidence_rows = [
            {
                "evidence_name": "global_bottleneck",
                "actual": {
                    "acceptance_posture": bottleneck_summary.get("acceptance_posture"),
                    "current_primary_bottleneck": bottleneck_summary.get("current_primary_bottleneck"),
                },
                "reading": "The current V1.2 bottleneck has not changed and still points to missing carry row diversity.",
            },
            {
                "evidence_name": "v6_first_lane_phase_check",
                "actual": {
                    "acceptance_posture": first_lane_phase_summary.get("acceptance_posture"),
                    "do_open_second_v6_lane_now": first_lane_phase_summary.get("do_open_second_v6_lane_now"),
                },
                "reading": "The first local v6 review already blocks second-lane widening because the first lane only closed as opening-led.",
            },
            {
                "evidence_name": "v6_reassessment",
                "actual": {
                    "acceptance_posture": v6_reassessment_summary.get("acceptance_posture"),
                    "do_open_second_v6_lane_now": v6_reassessment_summary.get("do_open_second_v6_lane_now"),
                    "do_prepare_next_refresh_now": v6_reassessment_summary.get("do_prepare_next_refresh_now"),
                },
                "reading": "The second review keeps v6 active but still blocks local widening and does not license a new refresh automatically.",
            },
        ]
        interpretation = [
            "V1.2 still has the same primary bottleneck, but the current legal local actions inside v6 are exhausted.",
            "Two consecutive phase-level reviews have not changed that bottleneck judgment, so forcing a new branch would violate the autonomy policy.",
            "The correct posture is to enter explicit waiting state until a new trigger, new legal high-value action, or owner-directed phase switch appears.",
        ]
        return V12WaitingStateSummaryReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_waiting_state_summary_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12WaitingStateSummaryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
