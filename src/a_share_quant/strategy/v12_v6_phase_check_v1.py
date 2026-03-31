from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12V6PhaseCheckReport:
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


class V12V6PhaseCheckAnalyzer:
    """Check whether v6 is ready to open its first bounded lane."""

    def analyze(
        self,
        *,
        manifest_payload: dict[str, Any],
        training_manifest_payload: dict[str, Any],
        specialist_analysis_payload: dict[str, Any],
        catalyst_phase_check_payload: dict[str, Any],
    ) -> V12V6PhaseCheckReport:
        manifest_summary = dict(manifest_payload.get("summary", {}))
        training_rows = list(training_manifest_payload.get("manifest_rows", []))
        top_rows = list(specialist_analysis_payload.get("top_opportunities", []))
        catalyst_summary = dict(catalyst_phase_check_payload.get("summary", {}))

        carry_rows_needed = 0
        persistence_rows_needed = 0
        for row in training_rows:
            class_name = str(row.get("class_name", ""))
            if class_name == "carry_row_present":
                carry_rows_needed = int(row.get("additional_rows_needed", 0))
            elif class_name == "persistence_led":
                persistence_rows_needed = int(row.get("additional_rows_needed", 0))

        v6_best_row = next(
            (
                row
                for row in top_rows
                if str(row.get("dataset_name", "")) == "market_research_v6_catalyst_supported_carry_persistence_refresh"
                and str(row.get("specialist_candidate", "")) == "baseline_expansion_branch"
            ),
            None,
        )

        open_first_lane_now = (
            bool(
                manifest_summary.get(
                    "ready_to_bootstrap_market_research_v6_catalyst_supported_carry_persistence_refresh"
                )
            )
            and v6_best_row is not None
            and carry_rows_needed > 0
            and persistence_rows_needed > 0
            and bool(catalyst_summary.get("keep_branch_report_only", True))
        )

        summary = {
            "acceptance_posture": (
                "open_first_v6_bounded_lane_on_best_specialist_pocket"
                if open_first_lane_now
                else "hold_v6_after_bootstrap"
            ),
            "v6_manifest_ready": bool(
                manifest_summary.get(
                    "ready_to_bootstrap_market_research_v6_catalyst_supported_carry_persistence_refresh"
                )
            ),
            "v6_active_in_specialist_map": v6_best_row is not None,
            "carry_rows_still_needed": carry_rows_needed,
            "persistence_rows_still_needed": persistence_rows_needed,
            "catalyst_branch_support_only": bool(catalyst_summary.get("keep_branch_report_only", True)),
            "do_open_first_v6_lane_now": open_first_lane_now,
            "do_widen_v6_now": False,
            "recommended_slice_name": str(v6_best_row.get("slice_name")) if v6_best_row else None,
            "recommended_strategy_name": str(v6_best_row.get("strategy_name")) if v6_best_row else None,
            "recommended_specialist_candidate": str(v6_best_row.get("specialist_candidate")) if v6_best_row else None,
        }
        evidence_rows = [
            {
                "evidence_name": "v6_manifest_status",
                "actual": {
                    "v6_manifest_ready": summary["v6_manifest_ready"],
                },
                "reading": "The first v6 lane only becomes legal after the new catalyst-supported batch is fully bootstrap-ready.",
            },
            {
                "evidence_name": "specialist_map_position",
                "actual": {
                    "v6_best_row": v6_best_row,
                },
                "reading": "V6 should open from the strongest current specialist pocket instead of from a generic lane guess.",
            },
            {
                "evidence_name": "training_gap_and_branch_role",
                "actual": {
                    "carry_rows_still_needed": carry_rows_needed,
                    "persistence_rows_still_needed": persistence_rows_needed,
                    "catalyst_branch_support_only": catalyst_summary.get("keep_branch_report_only"),
                },
                "reading": "The first v6 lane stays tied to the unresolved training gaps, with catalyst context supporting rather than replacing the mainline objective.",
            },
        ]
        interpretation = [
            "V6 is now a real substrate in the specialist map, so it is legal to open one bounded lane if the current map still shows unresolved carry and persistence gaps.",
            "That lane should come from the strongest current v6 specialist pocket, not from broad widening or from a catalyst-led branch switch.",
            "So the next healthy move is one bounded v6 lane on the best specialist pocket, with all widening still disallowed.",
        ]
        return V12V6PhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_v6_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12V6PhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
