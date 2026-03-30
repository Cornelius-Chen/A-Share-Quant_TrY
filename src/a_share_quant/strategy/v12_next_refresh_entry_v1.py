from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12NextRefreshEntryReport:
    summary: dict[str, Any]
    entry_rules: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "entry_rules": self.entry_rules,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V12NextRefreshEntryAnalyzer:
    """Turn the current V1.2 bottleneck into an executable next-refresh entry posture."""

    def analyze(
        self,
        *,
        bottleneck_payload: dict[str, Any],
        next_refresh_design_payload: dict[str, Any],
        v3_audit_payload: dict[str, Any],
        first_lane_acceptance_payload: dict[str, Any],
    ) -> V12NextRefreshEntryReport:
        bottleneck_summary = dict(bottleneck_payload.get("summary", {}))
        design_summary = dict(next_refresh_design_payload.get("summary", {}))
        audit_summary = dict(v3_audit_payload.get("summary", {}))
        lane_summary = dict(first_lane_acceptance_payload.get("summary", {}))

        bottleneck_is_carry_gap = (
            str(bottleneck_summary.get("current_primary_bottleneck")) == "carry_row_diversity_gap"
        )
        v3_is_ready = bool(audit_summary.get("baseline_ready"))
        first_lane_opening_led = bool(bottleneck_summary.get("first_lane_opening_led"))
        lane_changes_carry_reading = bool(lane_summary.get("lane_changes_carry_reading"))

        prepare_refresh_entry = bottleneck_is_carry_gap and v3_is_ready and not lane_changes_carry_reading
        next_batch_name = "market_research_v4_carry_row_diversity_refresh"

        summary = {
            "acceptance_posture": (
                "prepare_v12_next_refresh_entry_for_market_research_v4"
                if prepare_refresh_entry
                else "hold_v12_next_refresh_entry_until_bottleneck_is_stable"
            ),
            "prepare_refresh_entry_now": prepare_refresh_entry,
            "prepare_manifest_now": False,
            "current_primary_bottleneck": bottleneck_summary.get("current_primary_bottleneck"),
            "v3_baseline_ready": v3_is_ready,
            "first_lane_opening_led": first_lane_opening_led,
            "lane_changes_carry_reading": lane_changes_carry_reading,
            "recommended_next_batch_name": next_batch_name,
            "recommended_batch_posture": "criteria_first_carry_row_diversity_refresh",
        }
        entry_rules = [
            {
                "rule_name": "batch_scope",
                "rule_value": {
                    "next_batch_name": next_batch_name,
                    "prepare_manifest_now": False,
                    "keep_second_v3_lane_closed": True,
                },
                "reading": "The next refresh should open as a criteria-first entry, not as an immediate manifest expansion while the current v3 map remains intentionally narrow.",
            },
            {
                "rule_name": "selection_targets",
                "rule_value": {
                    "basis_spread_diversity": True,
                    "carry_duration_diversity": True,
                    "exit_alignment_diversity": True,
                    "cross_dataset_carry_reuse": True,
                },
                "reading": "The next refresh still has to target the same four carry row-diversity gaps; the first v3 lane did not replace them with a new priority.",
            },
            {
                "rule_name": "explicit_exclusions",
                "rule_value": {
                    "exclude_pure_opening_led_clones_as_primary_goal": True,
                    "exclude_general_sample_growth_as_primary_goal": True,
                    "exclude_second_factor_lane_opening": True,
                },
                "reading": "The next refresh should not drift into generic sample growth or capture-opening expansion just because the first v3 lane was opening-led.",
            },
        ]
        interpretation = [
            "The first v3 lane proved the new substrate is alive, but it did not solve the carry-lane bottleneck.",
            "So the right next move is to prepare the next refresh as a criteria-first carry-row-diversity entry rather than widen the current v3 replay map.",
            "This keeps V1.2 on its intended track: improve factor-row diversity first, then revisit whether the carry lane can become more than a report-only micro-pilot.",
        ]
        return V12NextRefreshEntryReport(
            summary=summary,
            entry_rules=entry_rules,
            interpretation=interpretation,
        )


def write_v12_next_refresh_entry_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12NextRefreshEntryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
