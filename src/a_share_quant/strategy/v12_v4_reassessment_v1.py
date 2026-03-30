from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12V4ReassessmentReport:
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


class V12V4ReassessmentAnalyzer:
    """Reassess the role of v4 after the checked high-priority hunt region pauses."""

    def analyze(
        self,
        *,
        v4_hunt_phase_check_payload: dict[str, Any],
        specialist_analysis_payload: dict[str, Any],
        bottleneck_check_payload: dict[str, Any],
    ) -> V12V4ReassessmentReport:
        hunt_summary = dict(v4_hunt_phase_check_payload.get("summary", {}))
        specialist_rows = list(specialist_analysis_payload.get("top_opportunities", []))
        bottleneck_summary = dict(bottleneck_check_payload.get("summary", {}))

        v4_top_rows = [
            row
            for row in specialist_rows
            if str(row.get("dataset_name", "")) == "market_research_v4_carry_row_diversity_refresh"
        ]
        v4_still_active_substrate = bool(v4_top_rows)
        checked_region_paused = (
            str(hunt_summary.get("acceptance_posture", ""))
            == "pause_v4_lower_priority_tracks_and_reassess_after_high_priority_hunt"
        )
        primary_bottleneck_still_carry = (
            str(bottleneck_summary.get("acceptance_posture", ""))
            == "keep_v12_primary_bottleneck_as_carry_row_diversity_gap"
        )

        summary = {
            "acceptance_posture": "keep_v4_as_active_but_locally_exhausted_substrate",
            "v4_still_active_substrate": v4_still_active_substrate,
            "checked_region_paused": checked_region_paused,
            "primary_bottleneck_still_carry_row_diversity": primary_bottleneck_still_carry,
            "do_open_lower_priority_v4_tracks_now": False,
            "do_open_new_v4_slice_now": False,
            "do_open_new_refresh_now": False,
            "recommended_next_posture": "return_to_v12_level_batch_or_substrate_decision",
        }
        evidence_rows = [
            {
                "evidence_name": "v4_hunt_phase_check",
                "actual": {
                    "checked_region_paused": checked_region_paused,
                    "high_priority_tracks_exhausted": hunt_summary.get("high_priority_tracks_exhausted"),
                    "all_checked_high_priority_hunts_inactive": hunt_summary.get("all_checked_high_priority_hunts_inactive"),
                },
                "reading": "The currently checked q2/A hunt area should not be extended automatically once its high-priority tracks are exhausted.",
            },
            {
                "evidence_name": "v4_specialist_map_position",
                "actual": {
                    "v4_still_active_substrate": v4_still_active_substrate,
                    "v4_top_opportunity_count": len(v4_top_rows),
                    "top_v4_rows": v4_top_rows[:1],
                },
                "reading": "V4 can remain a real substrate in the broader map even if one checked hunt area is locally exhausted.",
            },
            {
                "evidence_name": "global_v12_bottleneck",
                "actual": {
                    "primary_bottleneck_still_carry_row_diversity": primary_bottleneck_still_carry,
                },
                "reading": "The global V1.2 problem stays the same even when the local v4 q2/A hunt pauses.",
            },
        ]
        interpretation = [
            "V4 should not be discarded: it still exists as an active substrate inside the wider specialist map.",
            "But the checked v4 q2/A high-priority hunt region is now locally exhausted, so pushing into lower-priority tracks would look like replay drift.",
            "The correct next move is to return to a higher-level V1.2 decision about the next batch or substrate, not to force more v4 symbol hunts right now.",
        ]
        return V12V4ReassessmentReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_v4_reassessment_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12V4ReassessmentReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
