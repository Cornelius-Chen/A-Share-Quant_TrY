from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12V5ReassessmentReport:
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


class V12V5ReassessmentAnalyzer:
    """Reassess v5 after the first lane plus the clean-persistence track checks."""

    def analyze(
        self,
        *,
        manifest_payload: dict[str, Any],
        first_lane_payload: dict[str, Any],
        phase_check_payload: dict[str, Any],
        second_lane_payload: dict[str, Any],
        third_lane_payload: dict[str, Any],
    ) -> V12V5ReassessmentReport:
        manifest_rows = list(manifest_payload.get("manifest_rows", []))
        first_summary = dict(first_lane_payload.get("summary", {}))
        phase_summary = dict(phase_check_payload.get("summary", {}))
        second_summary = dict(second_lane_payload.get("summary", {}))
        third_summary = dict(third_lane_payload.get("summary", {}))

        clean_persistence_symbols = [
            str(row.get("symbol")) for row in manifest_rows if str(row.get("target_training_gap")) == "clean_persistence_row"
        ]
        true_carry_symbols = [
            str(row.get("symbol")) for row in manifest_rows if str(row.get("target_training_gap")) == "true_carry_row"
        ]

        clean_persistence_exhausted = (
            str(second_summary.get("acceptance_posture")) in {
                "close_market_v5_q2_second_lane_as_divergent_but_not_acceptance_grade",
                "close_market_v5_q2_second_lane_as_no_active_structural_lane",
                "close_market_v5_q2_second_lane_as_opening_led_not_clean_persistence",
            }
            and str(third_summary.get("acceptance_posture")) in {
                "close_market_v5_q2_second_lane_as_divergent_but_not_acceptance_grade",
                "close_market_v5_q2_second_lane_as_no_active_structural_lane",
                "close_market_v5_q2_second_lane_as_opening_led_not_clean_persistence",
            }
        )

        remaining_true_carry_symbols = [
            symbol
            for symbol in true_carry_symbols
            if symbol != str(first_summary.get("top_driver"))
        ]
        recommended_next_symbol = remaining_true_carry_symbols[0] if remaining_true_carry_symbols else ""

        open_last_true_carry_probe = (
            bool(phase_summary.get("do_open_second_v5_lane_now"))
            and bool(first_summary.get("opening_present"))
            and not bool(first_summary.get("lane_changes_carry_reading"))
            and clean_persistence_exhausted
            and bool(recommended_next_symbol)
        )

        summary = {
            "acceptance_posture": (
                "open_last_v5_true_carry_probe_after_persistence_track_exhaustion"
                if open_last_true_carry_probe
                else "pause_v5_after_reassessment"
            ),
            "first_lane_opening_led": bool(first_summary.get("opening_present"))
            and not bool(first_summary.get("persistence_present")),
            "clean_persistence_track_exhausted": clean_persistence_exhausted,
            "remaining_true_carry_symbols": remaining_true_carry_symbols,
            "do_open_last_true_carry_probe_now": open_last_true_carry_probe,
            "recommended_next_symbol": recommended_next_symbol,
            "do_open_new_refresh_now": False,
            "do_widen_v5_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "first_v5_lane",
                "actual": {
                    "top_driver": first_summary.get("top_driver"),
                    "opening_present": first_summary.get("opening_present"),
                    "persistence_present": first_summary.get("persistence_present"),
                    "lane_changes_carry_reading": first_summary.get("lane_changes_carry_reading"),
                },
                "reading": "The first v5 lane stayed opening-led, so the true-carry mission is still unresolved.",
            },
            {
                "evidence_name": "clean_persistence_track",
                "actual": {
                    "clean_persistence_symbols": clean_persistence_symbols,
                    "second_lane_acceptance": second_summary.get("acceptance_posture"),
                    "third_lane_acceptance": third_summary.get("acceptance_posture"),
                    "clean_persistence_track_exhausted": clean_persistence_exhausted,
                },
                "reading": "Once both clean-persistence symbols fail to produce an acceptance-grade persistence edge, the persistence track is locally exhausted.",
            },
            {
                "evidence_name": "remaining_true_carry_probe",
                "actual": {
                    "remaining_true_carry_symbols": remaining_true_carry_symbols,
                    "recommended_next_symbol": recommended_next_symbol,
                },
                "reading": "After the clean-persistence track exhausts, one bounded true-carry probe remains legal before any new refresh or broader replay decision.",
            },
        ]
        interpretation = [
            "V5 has not solved the carry-row-diversity bottleneck yet: its first lane is opening-led and its two clean-persistence probes failed to produce acceptance-grade persistence.",
            "That does not justify widening replay or opening a new refresh batch immediately.",
            "But one bounded true-carry probe still remains inside the current v5 manifest, so the correct next move is to test that final symbol before another higher-level V1.2 decision.",
        ]
        return V12V5ReassessmentReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_v5_reassessment_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12V5ReassessmentReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
