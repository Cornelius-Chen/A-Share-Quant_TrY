from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12V6ReassessmentReport:
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


class V12V6ReassessmentAnalyzer:
    """Reassess v6 after its first bounded lane closes without repairing the main gap."""

    def analyze(
        self,
        *,
        first_lane_phase_check_payload: dict[str, Any],
        specialist_analysis_payload: dict[str, Any],
        bottleneck_check_payload: dict[str, Any],
    ) -> V12V6ReassessmentReport:
        phase_check_summary = dict(first_lane_phase_check_payload.get("summary", {}))
        specialist_rows = list(specialist_analysis_payload.get("top_opportunities", []))
        bottleneck_summary = dict(bottleneck_check_payload.get("summary", {}))

        v6_top_rows = [
            row
            for row in specialist_rows
            if str(row.get("dataset_name", "")) == "market_research_v6_catalyst_supported_carry_persistence_refresh"
        ]
        v6_still_active_substrate = bool(v6_top_rows)
        primary_bottleneck_still_carry = (
            str(bottleneck_summary.get("acceptance_posture", ""))
            == "keep_v12_primary_bottleneck_as_carry_row_diversity_gap"
        )

        summary = {
            "acceptance_posture": "keep_v6_as_active_but_hold_local_second_lane_after_opening_first_lane",
            "v6_still_active_substrate": v6_still_active_substrate,
            "first_lane_phase_holds_local_expansion": not bool(
                phase_check_summary.get("do_open_second_v6_lane_now")
            ),
            "primary_bottleneck_still_carry_row_diversity": primary_bottleneck_still_carry,
            "do_open_second_v6_lane_now": False,
            "do_prepare_next_refresh_now": False,
            "recommended_next_posture": "return_to_v12_level_batch_or_substrate_decision",
        }
        evidence_rows = [
            {
                "evidence_name": "v6_first_lane_phase_check",
                "actual": {
                    "acceptance_posture": phase_check_summary.get("acceptance_posture"),
                    "do_open_second_v6_lane_now": phase_check_summary.get("do_open_second_v6_lane_now"),
                    "recommended_next_posture": phase_check_summary.get("recommended_next_posture"),
                },
                "reading": "The v6 local picture should not widen after an opening-only first lane when the remaining candidates do not improve enough.",
            },
            {
                "evidence_name": "v6_specialist_map_position",
                "actual": {
                    "v6_still_active_substrate": v6_still_active_substrate,
                    "v6_top_opportunity_count": len(v6_top_rows),
                    "top_v6_rows": v6_top_rows[:1],
                },
                "reading": "V6 can remain a real substrate in the wider specialist map even if its first local lane does not yet justify a second local probe.",
            },
            {
                "evidence_name": "global_v12_bottleneck",
                "actual": {
                    "primary_bottleneck_still_carry_row_diversity": primary_bottleneck_still_carry,
                },
                "reading": "The global V1.2 problem remains the carry-row-diversity gap, so local widening still needs a stronger structure than an opening-only first lane.",
            },
        ]
        interpretation = [
            "V6 remains a valid active substrate, so this is not a batch failure.",
            "But its first local lane only closed as opening-led, and the current local candidate set does not justify automatic second-lane expansion.",
            "The correct posture is to hold local widening and return to a higher-level V1.2 batch or substrate decision.",
        ]
        return V12V6ReassessmentReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_v6_reassessment_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12V6ReassessmentReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
