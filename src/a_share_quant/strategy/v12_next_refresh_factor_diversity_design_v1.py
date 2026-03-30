from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12NextRefreshFactorDiversityDesignReport:
    summary: dict[str, Any]
    target_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "target_rows": self.target_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V12NextRefreshFactorDiversityDesignAnalyzer:
    """Design the next refresh batch around missing factor-row diversity."""

    def analyze(
        self,
        *,
        phase_readiness_payload: dict[str, Any],
        carry_pilot_payload: dict[str, Any],
        carry_schema_payload: dict[str, Any],
    ) -> V12NextRefreshFactorDiversityDesignReport:
        phase_summary = dict(phase_readiness_payload.get("summary", {}))
        carry_pilot_summary = dict(carry_pilot_payload.get("summary", {}))
        carry_schema_summary = dict(carry_schema_payload.get("summary", {}))

        if not bool(phase_summary.get("do_open_new_refresh_batch_now")):
            raise ValueError("Next-refresh factor-diversity design only opens when V1.2 readiness requires a later refresh batch.")
        if not bool(carry_pilot_summary.get("needs_more_row_diversity_for_rankable_pilot")):
            raise ValueError("Carry pilot must still be row-diversity constrained before opening this design.")

        target_rows = [
            {
                "priority": 1,
                "target_name": "basis_spread_diversity",
                "target_posture": "add_carry_rows_with_lower_and_mid_basis_advantage",
                "desired_shift": "basis_advantage_bps should no longer collapse to one saturated value.",
                "rationale": "The current carry rows both saturate the basis component. The next refresh should add rows that create non-maximal basis values.",
            },
            {
                "priority": 2,
                "target_name": "carry_duration_diversity",
                "target_posture": "add_rows_with_zero_or_multi_day_carry_variation",
                "desired_shift": "challenger_carry_days should vary beyond the current constant +1 day.",
                "rationale": "The current pilot cannot learn whether carry is robust when duration is shorter or longer than the current shared row shape.",
            },
            {
                "priority": 3,
                "target_name": "exit_alignment_diversity",
                "target_posture": "seek_rows_where_same_exit_date_can_break",
                "desired_shift": "same_exit_date should not remain uniformly true across all carry rows.",
                "rationale": "A rankable pilot needs evidence beyond the current perfect same-exit alignment pattern.",
            },
            {
                "priority": 4,
                "target_name": "cross_dataset_carry_reuse",
                "target_posture": "add_non_theme_q4_candidates_with_carry_like_negative_cycle_basis",
                "desired_shift": "carry rows should appear outside the current theme_q4 / 300750 evidence island.",
                "rationale": "The next refresh should expand carry evidence beyond one dataset-slice-symbol cluster before any wider factor work opens.",
            },
        ]

        summary = {
            "design_posture": "prepare_refresh_batch_for_factor_row_diversity",
            "target_count": len(target_rows),
            "current_carry_schema_row_count": carry_schema_summary.get("schema_row_count"),
            "current_distinct_score_count": carry_pilot_summary.get("distinct_score_count"),
            "row_diversity_gap_confirmed": True,
            "recommended_next_batch_name": "market_research_v3_factor_diversity_seed",
            "recommended_batch_posture": "expand_for_carry_row_diversity_not_general_size",
            "do_prepare_new_refresh_manifest": True,
        }
        interpretation = [
            "The next refresh batch should not be justified as generic sample growth; it should be justified as targeted factor-row diversity expansion.",
            "The carry lane is currently bottlenecked by saturated basis values, constant carry duration, and perfect same-exit alignment.",
            "So the next batch should be designed to break those constants before any second factor lane is opened.",
        ]
        return V12NextRefreshFactorDiversityDesignReport(
            summary=summary,
            target_rows=target_rows,
            interpretation=interpretation,
        )


def write_v12_next_refresh_factor_diversity_design_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12NextRefreshFactorDiversityDesignReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
