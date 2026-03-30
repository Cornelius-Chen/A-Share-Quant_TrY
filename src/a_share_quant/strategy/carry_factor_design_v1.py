from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CarryFactorDesignReport:
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


class CarryFactorDesignAnalyzer:
    """Translate the carry first-pass result into a bounded factor-design posture."""

    def analyze(
        self,
        *,
        first_pass_payload: dict[str, Any],
        mechanism_b_payload: dict[str, Any],
        mechanism_c_payload: dict[str, Any],
        cross_strategy_payload: dict[str, Any],
    ) -> CarryFactorDesignReport:
        first_pass_summary = dict(first_pass_payload.get("summary", {}))
        mechanism_b_rows = mechanism_b_payload.get("mechanism_rows", [])
        mechanism_c_rows = mechanism_c_payload.get("mechanism_rows", [])
        if not isinstance(mechanism_b_rows, list) or not isinstance(mechanism_c_rows, list):
            raise ValueError("Mechanism payloads must contain mechanism_rows.")

        def mechanism_types(rows: list[dict[str, Any]]) -> set[str]:
            return {str(row.get("mechanism_type")) for row in rows if row.get("mechanism_type")}

        b_types = mechanism_types(mechanism_b_rows)
        c_types = mechanism_types(mechanism_c_rows)
        shared_types = sorted(b_types & c_types)

        carry_lane_open = bool(first_pass_summary.get("do_open_bounded_carry_factor_lane"))
        carry_shared = "carry_in_basis_advantage" in shared_types
        mixed_with_earlier_exit = "earlier_exit_loss_reduction" in shared_types
        row_isolation_required = carry_shared and mixed_with_earlier_exit
        identical_negative_map = bool(
            cross_strategy_payload.get("summary", {}).get("identical_negative_cycle_map", False)
        )

        design_posture = (
            "open_row_isolated_carry_factor_design"
            if carry_lane_open and carry_shared
            else "hold_carry_factor_design"
        )
        summary = {
            "design_posture": design_posture,
            "do_open_carry_factor_design": design_posture
            == "open_row_isolated_carry_factor_design",
            "carry_lane_open": carry_lane_open,
            "carry_shared_across_b_c": carry_shared,
            "mixed_with_earlier_exit": mixed_with_earlier_exit,
            "row_isolation_required": row_isolation_required,
            "identical_negative_cycle_map": identical_negative_map,
            "allow_broad_factor_scoring_now": False,
            "allow_retained_feature_promotion_now": False,
            "next_design_mode": "negative_cycle_basis_row_isolation",
        }
        evidence_rows = [
            {
                "evidence_name": "first_pass_gate",
                "actual": first_pass_summary,
                "reading": "The design lane only opens after the bounded first-pass gate is already green.",
            },
            {
                "evidence_name": "shared_mechanism_mix",
                "actual": {
                    "mechanism_types_b": sorted(b_types),
                    "mechanism_types_c": sorted(c_types),
                    "shared_mechanism_types": shared_types,
                },
                "reading": "Carry repeats across B/C, but it coexists with earlier-exit reduction inside the same pocket family mix.",
            },
            {
                "evidence_name": "design_boundary",
                "actual": {
                    "row_isolation_required": row_isolation_required,
                    "identical_negative_cycle_map": identical_negative_map,
                },
                "reading": "Because carry is embedded in a mixed pocket, the next design should isolate carry rows rather than treat the whole pocket as one factor.",
            },
        ]
        interpretation = [
            "Carry is strong enough to open factor design, but not clean enough to inherit an entire mixed pocket unchanged.",
            "The right next move is a row-isolated negative-cycle basis design, not broad factor scoring across all current pockets.",
            "This keeps the lane narrow, preserves the protocol discipline, and avoids accidental promotion into retained-feature status.",
        ]
        return CarryFactorDesignReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_carry_factor_design_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CarryFactorDesignReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
