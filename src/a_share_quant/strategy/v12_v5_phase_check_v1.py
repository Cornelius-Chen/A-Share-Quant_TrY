from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12V5PhaseCheckReport:
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


class V12V5PhaseCheckAnalyzer:
    """Check whether the first v5 lane justifies a second bounded v5 lane."""

    def analyze(
        self,
        *,
        manifest_payload: dict[str, Any],
        training_manifest_payload: dict[str, Any],
        first_lane_payload: dict[str, Any],
        divergence_payload: dict[str, Any],
    ) -> V12V5PhaseCheckReport:
        manifest_summary = dict(manifest_payload.get("summary", {}))
        manifest_rows = list(manifest_payload.get("manifest_rows", []))
        training_summary = dict(training_manifest_payload.get("summary", {}))
        training_rows = list(training_manifest_payload.get("manifest_rows", []))
        lane_summary = dict(first_lane_payload.get("summary", {}))
        divergence_rows = list(divergence_payload.get("strategy_symbol_summary", []))

        carry_rows_needed = int(training_summary.get("additional_carry_rows_needed", 0))
        persistence_rows_needed = int(training_summary.get("additional_persistence_rows_needed", 0))
        first_lane_opening_led = bool(lane_summary.get("opening_present")) and not bool(
            lane_summary.get("persistence_present")
        )
        lane_changes_carry_reading = bool(lane_summary.get("lane_changes_carry_reading"))

        clean_persistence_candidates = {
            str(row.get("symbol")) for row in manifest_rows if str(row.get("target_training_gap")) == "clean_persistence_row"
        }
        ranked_nonzero = sorted(
            (
                row
                for row in divergence_rows
                if str(row.get("symbol")) in clean_persistence_candidates
                and abs(float(row.get("pnl_delta", 0.0))) > 0.0
            ),
            key=lambda item: abs(float(item.get("pnl_delta", 0.0))),
            reverse=True,
        )
        recommended_next_symbol = str(ranked_nonzero[0]["symbol"]) if ranked_nonzero else None

        open_second_lane_now = (
            first_lane_opening_led
            and not lane_changes_carry_reading
            and carry_rows_needed > 0
            and persistence_rows_needed > 0
            and recommended_next_symbol is not None
        )

        summary = {
            "acceptance_posture": (
                "open_second_v5_lane_on_clean_persistence_track"
                if open_second_lane_now
                else "hold_v5_after_first_lane"
            ),
            "v5_manifest_ready": bool(
                manifest_summary.get("ready_to_bootstrap_market_research_v5_carry_row_diversity_refresh")
            ),
            "first_lane_opening_led": first_lane_opening_led,
            "lane_changes_carry_reading": lane_changes_carry_reading,
            "additional_carry_rows_needed": carry_rows_needed,
            "additional_persistence_rows_needed": persistence_rows_needed,
            "do_open_second_v5_lane_now": open_second_lane_now,
            "do_widen_v5_now": False,
            "recommended_next_track": "clean_persistence_row" if open_second_lane_now else None,
            "recommended_next_symbol": recommended_next_symbol,
        }
        evidence_rows = [
            {
                "evidence_name": "first_v5_lane",
                "actual": {
                    "top_driver": lane_summary.get("top_driver"),
                    "opening_present": lane_summary.get("opening_present"),
                    "persistence_present": lane_summary.get("persistence_present"),
                    "lane_changes_carry_reading": lane_summary.get("lane_changes_carry_reading"),
                },
                "reading": "The first v5 lane closed as opening-led and therefore did not satisfy the carry-gap mission by itself.",
            },
            {
                "evidence_name": "training_gap_manifest",
                "actual": {
                    "additional_carry_rows_needed": carry_rows_needed,
                    "additional_persistence_rows_needed": persistence_rows_needed,
                    "opening_count_frozen": training_summary.get("opening_count_frozen"),
                },
                "reading": "Opening is frozen; only true carry rows and clean persistence rows are valid next training-gap targets.",
            },
            {
                "evidence_name": "clean_persistence_candidates",
                "actual": {
                    "candidate_symbols": sorted(clean_persistence_candidates),
                    "ranked_nonzero_symbols": [
                        {
                            "symbol": str(row.get("symbol")),
                            "pnl_delta": float(row.get("pnl_delta", 0.0)),
                        }
                        for row in ranked_nonzero
                    ],
                },
                "reading": "If a second lane is opened, it should pivot to the clean-persistence track rather than keep chasing another nominal carry symbol after the first lane closes as opening-led.",
            },
        ]
        interpretation = [
            "The first v5 lane does not justify broadening replay or reclassifying the substrate as carry-resolved.",
            "But because the training-gap manifest still needs both carry and persistence rows, a single bounded second lane remains legal if it stays inside the clean-persistence track.",
            "So the correct next move is one more v5 lane on the clean-persistence track, not a wider v5 replay expansion.",
        ]
        return V12V5PhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_v5_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12V5PhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
