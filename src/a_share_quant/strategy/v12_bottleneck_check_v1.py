from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12BottleneckCheckReport:
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


class V12BottleneckCheckAnalyzer:
    """Check whether the first v3 lane changes the current V1.2 bottleneck reading."""

    def analyze(
        self,
        *,
        phase_readiness_payload: dict[str, Any],
        next_refresh_design_payload: dict[str, Any],
        first_lane_acceptance_payload: dict[str, Any],
    ) -> V12BottleneckCheckReport:
        phase_summary = dict(phase_readiness_payload.get("summary", {}))
        design_summary = dict(next_refresh_design_payload.get("summary", {}))
        lane_summary = dict(first_lane_acceptance_payload.get("summary", {}))

        row_diversity_still_missing = bool(phase_summary.get("row_diversity_still_missing"))
        refresh_batch_still_needed = bool(phase_summary.get("do_open_new_refresh_batch_now"))
        lane_changes_carry_reading = bool(lane_summary.get("lane_changes_carry_reading"))
        opening_present = bool(lane_summary.get("opening_present"))
        persistence_present = bool(lane_summary.get("persistence_present"))

        bottleneck_unchanged = (
            row_diversity_still_missing
            and refresh_batch_still_needed
            and not lane_changes_carry_reading
            and opening_present
            and not persistence_present
        )

        summary = {
            "acceptance_posture": (
                "keep_v12_primary_bottleneck_as_carry_row_diversity_gap"
                if bottleneck_unchanged
                else "reassess_v12_primary_bottleneck_after_v3_first_lane"
            ),
            "row_diversity_still_missing": row_diversity_still_missing,
            "refresh_batch_still_needed": refresh_batch_still_needed,
            "lane_changes_carry_reading": lane_changes_carry_reading,
            "first_lane_opening_led": opening_present and not persistence_present,
            "current_primary_bottleneck": (
                "carry_row_diversity_gap"
                if bottleneck_unchanged
                else "reassessment_needed"
            ),
            "do_open_second_v3_lane_now": False,
            "do_change_v12_direction_now": False,
            "recommended_next_posture": (
                "keep_v12_on_factor_row_diversity_track"
                if bottleneck_unchanged
                else "reassess_v12_track_before_new_lane"
            ),
            "recommended_next_batch_name": design_summary.get("recommended_next_batch_name"),
        }
        evidence_rows = [
            {
                "evidence_name": "phase_readiness",
                "actual": {
                    "row_diversity_still_missing": row_diversity_still_missing,
                    "do_open_new_refresh_batch_now": refresh_batch_still_needed,
                    "recommended_next_posture": phase_summary.get("recommended_next_posture"),
                },
                "reading": "If the phase gate still says row diversity is missing, one new lane needs to overturn that reading before the main bottleneck can change.",
            },
            {
                "evidence_name": "next_refresh_design",
                "actual": {
                    "design_posture": design_summary.get("design_posture"),
                    "recommended_batch_posture": design_summary.get("recommended_batch_posture"),
                    "recommended_next_batch_name": design_summary.get("recommended_next_batch_name"),
                },
                "reading": "The last V1.2 design step already narrowed the next batch goal to carry row diversity rather than generic expansion.",
            },
            {
                "evidence_name": "first_v3_lane",
                "actual": {
                    "top_driver": lane_summary.get("top_driver"),
                    "opening_present": opening_present,
                    "persistence_present": persistence_present,
                    "lane_changes_carry_reading": lane_changes_carry_reading,
                },
                "reading": "An opening-led first lane without a clean persistence edge does not yet count as carry-breakthrough evidence.",
            },
        ]
        interpretation = [
            "The first v3 lane is useful because it proves the new substrate can generate live specialist lanes, but it does not yet solve the carry-lane bottleneck.",
            "Because the lane closes as opening-led and does not change the carry reading, V1.2 should keep its primary bottleneck defined as missing carry row diversity.",
            "So the correct next posture is not to widen replay, but to stay on the factor-row-diversity track until a later lane or later refresh batch materially changes that reading.",
        ]
        return V12BottleneckCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_bottleneck_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12BottleneckCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
