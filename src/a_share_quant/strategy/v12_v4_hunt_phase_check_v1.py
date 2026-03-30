from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12V4HuntPhaseCheckReport:
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


class V12V4HuntPhaseCheckAnalyzer:
    """Check whether the current v4 q2/A carry hunt should pause before lower-priority tracks."""

    def analyze(
        self,
        *,
        hunting_strategy_payload: dict[str, Any],
        bottleneck_check_payload: dict[str, Any],
        first_hunt_payload: dict[str, Any],
        second_hunt_payload: dict[str, Any],
        third_hunt_payload: dict[str, Any],
        fourth_hunt_payload: dict[str, Any],
    ) -> V12V4HuntPhaseCheckReport:
        hunt_rows = list(hunting_strategy_payload.get("hunt_rows", []))
        bottleneck_summary = dict(bottleneck_check_payload.get("summary", {}))
        checked_payloads = [
            dict(first_hunt_payload.get("summary", {})),
            dict(second_hunt_payload.get("summary", {})),
            dict(third_hunt_payload.get("summary", {})),
            dict(fourth_hunt_payload.get("summary", {})),
        ]

        high_priority_targets = [
            row
            for row in hunt_rows
            if str(row.get("target_row_diversity", "")) in {"basis_spread_diversity", "carry_duration_diversity"}
        ]
        checked_symbols = [str(row.get("target_symbol", "")) for row in checked_payloads]
        checked_high_priority_count = sum(
            1 for row in high_priority_targets if str(row.get("symbol", "")) in checked_symbols
        )
        high_priority_target_count = len(high_priority_targets)

        all_checked_inactive = all(
            str(row.get("acceptance_posture", "")) == "close_market_v4_q2_symbol_hunt_as_no_active_structural_lane"
            and not bool(row.get("lane_changes_carry_reading"))
            for row in checked_payloads
        )
        high_priority_tracks_exhausted = (
            high_priority_target_count > 0 and checked_high_priority_count == high_priority_target_count
        )
        primary_bottleneck_still_carry = (
            str(bottleneck_summary.get("acceptance_posture", ""))
            == "keep_v12_primary_bottleneck_as_carry_row_diversity_gap"
        )

        pause_before_lower_priority = (
            high_priority_tracks_exhausted
            and all_checked_inactive
            and primary_bottleneck_still_carry
        )

        summary = {
            "acceptance_posture": (
                "pause_v4_lower_priority_tracks_and_reassess_after_high_priority_hunt"
                if pause_before_lower_priority
                else "continue_v4_symbol_hunt"
            ),
            "high_priority_target_count": high_priority_target_count,
            "checked_high_priority_count": checked_high_priority_count,
            "high_priority_tracks_exhausted": high_priority_tracks_exhausted,
            "all_checked_high_priority_hunts_inactive": all_checked_inactive,
            "primary_bottleneck_still_carry_row_diversity": primary_bottleneck_still_carry,
            "do_open_lower_priority_tracks_now": False if pause_before_lower_priority else True,
            "do_open_new_refresh_now": False,
            "recommended_next_posture": (
                "reassess_v4_hunt_posture_before_cross_dataset_or_exit_alignment_tracks"
                if pause_before_lower_priority
                else "continue_v4_hunt"
            ),
        }
        evidence_rows = [
            {
                "evidence_name": "high_priority_track_coverage",
                "actual": {
                    "high_priority_target_count": high_priority_target_count,
                    "checked_high_priority_count": checked_high_priority_count,
                    "high_priority_tracks_exhausted": high_priority_tracks_exhausted,
                },
                "reading": "A pause is only justified if the checked hunt has already covered the intended high-priority carry tracks.",
            },
            {
                "evidence_name": "checked_hunt_outcomes",
                "actual": {
                    "checked_symbols": checked_symbols,
                    "all_checked_high_priority_hunts_inactive": all_checked_inactive,
                },
                "reading": "If every checked high-priority symbol closes inactive, blindly moving to lower-priority tracks risks replay drift rather than real carry discovery.",
            },
            {
                "evidence_name": "phase_bottleneck",
                "actual": {
                    "primary_bottleneck_still_carry_row_diversity": primary_bottleneck_still_carry,
                },
                "reading": "The main V1.2 bottleneck can remain carry row diversity even while a specific v4 hunt slice is temporarily exhausted.",
            },
        ]
        interpretation = [
            "The current v4 q2/A hunt has now checked the intended high-priority basis-spread and carry-duration targets without surfacing an active structural lane.",
            "That does not solve the main V1.2 bottleneck, but it does justify a pause before touching lower-priority tracks such as cross-dataset reuse or exit-alignment.",
            "So the correct next move is a short reassessment of the v4 hunt posture rather than another immediate symbol replay.",
        ]
        return V12V4HuntPhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_v4_hunt_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12V4HuntPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
