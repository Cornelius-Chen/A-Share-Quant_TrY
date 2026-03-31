from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MarketV5Q2SecondLaneAcceptanceReport:
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


class MarketV5Q2SecondLaneAcceptanceAnalyzer:
    """Close or continue the second bounded v5 lane on the clean-persistence track."""

    def analyze(
        self,
        *,
        target_symbol: str,
        next_symbol_if_closed: str,
        phase_check_payload: dict[str, Any],
        divergence_payload: dict[str, Any],
        opening_payload: dict[str, Any],
        persistence_payload: dict[str, Any],
    ) -> MarketV5Q2SecondLaneAcceptanceReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        divergence_rows = list(divergence_payload.get("strategy_symbol_summary", []))
        target_divergence = next(
            (row for row in divergence_rows if str(row.get("symbol")) == target_symbol),
            None,
        )
        if target_divergence is None:
            raise ValueError(f"Target symbol {target_symbol} is not present in the v5 divergence report.")

        target_delta = float(target_divergence.get("pnl_delta", 0.0))
        opening_summary = dict(opening_payload.get("summary", {}))
        persistence_summary = dict(persistence_payload.get("summary", {}))
        opening_present = bool(opening_summary.get("specialist_opened_window"))
        persistence_present = bool(persistence_summary.get("specialist_preserved_window"))

        if persistence_present:
            acceptance_posture = "close_market_v5_q2_second_lane_as_clean_persistence_candidate"
            lane_changes_training_reading = True
        elif opening_present:
            acceptance_posture = "close_market_v5_q2_second_lane_as_opening_led_not_clean_persistence"
            lane_changes_training_reading = False
        elif abs(target_delta) > 1e-9:
            acceptance_posture = "close_market_v5_q2_second_lane_as_divergent_but_not_acceptance_grade"
            lane_changes_training_reading = False
        else:
            acceptance_posture = "close_market_v5_q2_second_lane_as_no_active_structural_lane"
            lane_changes_training_reading = False

        summary = {
            "acceptance_posture": acceptance_posture,
            "target_symbol": target_symbol,
            "target_pnl_delta": target_delta,
            "opening_present": opening_present,
            "persistence_present": persistence_present,
            "lane_changes_training_reading": lane_changes_training_reading,
            "phase_allowed_second_lane": bool(phase_summary.get("do_open_second_v5_lane_now")),
            "do_continue_current_symbol_now": False,
            "do_open_third_v5_lane_now": not lane_changes_training_reading,
            "recommended_next_symbol": next_symbol_if_closed if not lane_changes_training_reading else "",
        }
        evidence_rows = [
            {
                "evidence_name": "phase_gate",
                "actual": {
                    "phase_acceptance_posture": phase_summary.get("acceptance_posture"),
                    "recommended_next_track": phase_summary.get("recommended_next_track"),
                    "phase_allowed_second_lane": phase_summary.get("do_open_second_v5_lane_now"),
                },
                "reading": "The second v5 lane is only legal because the phase check kept the batch bounded and redirected it to the clean-persistence track.",
            },
            {
                "evidence_name": "divergence_signature",
                "actual": {
                    "target_symbol": target_symbol,
                    "target_pnl_delta": target_delta,
                    "incumbent_trade_count": target_divergence.get("incumbent_trade_count"),
                    "challenger_trade_count": target_divergence.get("challenger_trade_count"),
                },
                "reading": "The clean-persistence target must show at least some structural divergence before persistence can be meaningfully checked.",
            },
            {
                "evidence_name": "window_checks",
                "actual": {
                    "opening_present": opening_present,
                    "opening_trade_date": opening_summary.get("opening_trade_date"),
                    "persistence_present": persistence_present,
                    "persistence_trade_date": persistence_summary.get("persistence_trade_date"),
                },
                "reading": "Only a clean persistence edge upgrades the second v5 lane into a training-gap-relevant result.",
            },
        ]
        interpretation = [
            "The second v5 lane exists to probe the clean-persistence track after the first v5 lane closed as opening-led.",
            "A second lane that only reproduces opening does not solve the training-gap problem even if it is structurally real.",
            "So the lane should only change the v5 reading when it surfaces a clean persistence edge; otherwise the batch stays bounded and moves to the last remaining clean-persistence symbol.",
        ]
        return MarketV5Q2SecondLaneAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_market_v5_q2_second_lane_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MarketV5Q2SecondLaneAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
