from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MarketV6Q3FirstLaneAcceptanceReport:
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


class MarketV6Q3FirstLaneAcceptanceAnalyzer:
    """Decide whether the first v6 lane changes the current carry/persistence reading."""

    def analyze(
        self,
        *,
        divergence_payload: dict[str, Any],
        opening_payload: dict[str, Any],
        persistence_payload: dict[str, Any],
    ) -> MarketV6Q3FirstLaneAcceptanceReport:
        divergence_rows = divergence_payload.get("strategy_symbol_summary", [])
        if not isinstance(divergence_rows, list):
            raise ValueError("Trade divergence payload must contain strategy_symbol_summary.")

        ranked_positive = sorted(
            (row for row in divergence_rows if float(row.get("pnl_delta", 0.0)) > 0.0),
            key=lambda item: float(item["pnl_delta"]),
            reverse=True,
        )
        top_positive_symbols = [str(row["symbol"]) for row in ranked_positive[:3]]
        top_driver = top_positive_symbols[0] if top_positive_symbols else None

        opening_summary = dict(opening_payload.get("summary", {}))
        opening_edge = dict(opening_payload.get("opening_edge") or {})
        persistence_summary = dict(persistence_payload.get("summary", {}))

        opening_present = bool(opening_summary.get("specialist_opened_window"))
        persistence_present = bool(persistence_summary.get("specialist_preserved_window"))

        lane_changes_training_reading = persistence_present
        if persistence_present:
            acceptance_posture = "close_market_v6_q3_first_lane_as_clean_persistence_not_true_carry"
        elif opening_present:
            acceptance_posture = "close_market_v6_q3_first_lane_as_opening_led_not_true_carry"
        elif top_driver == "600118" and ranked_positive:
            acceptance_posture = "close_market_v6_q3_first_lane_as_divergent_but_not_acceptance_grade"
        else:
            acceptance_posture = "close_market_v6_q3_first_lane_as_no_active_structural_lane"

        summary = {
            "acceptance_posture": acceptance_posture,
            "top_positive_symbols": top_positive_symbols,
            "top_driver": top_driver,
            "opening_present": opening_present,
            "persistence_present": persistence_present,
            "opening_trade_date": opening_summary.get("opening_trade_date"),
            "persistence_trade_date": persistence_summary.get("persistence_trade_date"),
            "specialist_assignment_layer": opening_edge.get("specialist_assignment_layer"),
            "lane_changes_training_reading": lane_changes_training_reading,
            "do_open_second_v6_lane_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "top_driver_rank",
                "actual": {
                    "top_driver": top_driver,
                    "top_positive_symbols": top_positive_symbols,
                },
                "reading": "The first v6 lane should be judged using the strongest q3/C symbol rather than widening to another lane.",
            },
            {
                "evidence_name": "opening_edge",
                "actual": {
                    "opening_present": opening_present,
                    "opening_trade_date": opening_summary.get("opening_trade_date"),
                    "specialist_assignment_layer": opening_edge.get("specialist_assignment_layer"),
                },
                "reading": "A clean opening-led reading requires a specialist-only admission edge that the anchors did not match at the same time.",
            },
            {
                "evidence_name": "persistence_check",
                "actual": {
                    "persistence_present": persistence_present,
                    "persistence_trade_date": persistence_summary.get("persistence_trade_date"),
                },
                "reading": "If the checked late window preserves the specialist position while anchors churn out, the lane may count as persistence-led support even if it is not true carry.",
            },
        ]
        interpretation = [
            "The first v6 lane should only improve the training reading if it contributes more than another opening-only case.",
            "A clean persistence edge is useful for the manifest even if it does not yet repair the carry gap itself.",
            "So the correct current posture is to classify the first v6 lane conservatively before any second-lane decision.",
        ]
        return MarketV6Q3FirstLaneAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_market_v6_q3_first_lane_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MarketV6Q3FirstLaneAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
