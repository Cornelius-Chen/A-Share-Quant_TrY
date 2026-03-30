from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MarketV4Q2FirstLaneAcceptanceReport:
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


class MarketV4Q2FirstLaneAcceptanceAnalyzer:
    """Decide whether the first v4 lane changes the current carry-row-diversity reading."""

    def analyze(
        self,
        *,
        divergence_payload: dict[str, Any],
        opening_payload: dict[str, Any],
        persistence_payload: dict[str, Any],
    ) -> MarketV4Q2FirstLaneAcceptanceReport:
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
        anchor_blockers = list(opening_payload.get("anchor_blockers", []))
        anchor_alignment = bool(anchor_blockers) and all(
            bool(row.get("permission_allowed")) and not list(row.get("emitted_actions", []))
            for row in anchor_blockers
        )
        anchor_junk_block = bool(anchor_blockers) and all(
            str(row.get("assignment_layer")) == "junk" for row in anchor_blockers
        )

        lane_changes_carry_reading = False
        acceptance_posture = (
            "close_market_v4_q2_first_lane_as_opening_led_not_carry_breakthrough"
            if opening_present and not persistence_present and top_driver == "601919"
            else "continue_market_v4_q2_first_lane_structural_check"
        )

        summary = {
            "acceptance_posture": acceptance_posture,
            "top_positive_symbols": top_positive_symbols,
            "top_driver": top_driver,
            "opening_present": opening_present,
            "persistence_present": persistence_present,
            "anchor_alignment_present": anchor_alignment,
            "anchor_junk_block_present": anchor_junk_block,
            "lane_changes_carry_reading": lane_changes_carry_reading,
            "do_open_second_v4_lane_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "top_driver_rank",
                "actual": {
                    "top_driver": top_driver,
                    "top_positive_symbols": top_positive_symbols,
                },
                "reading": "The first v4 lane should be judged using the strongest q2/A symbol rather than widening to another lane.",
            },
            {
                "evidence_name": "opening_edge",
                "actual": {
                    "opening_present": opening_present,
                    "opening_trade_date": opening_summary.get("opening_trade_date"),
                    "specialist_assignment_layer": opening_edge.get("specialist_assignment_layer"),
                    "anchor_alignment_present": anchor_alignment,
                    "anchor_junk_block_present": anchor_junk_block,
                },
                "reading": "A clean opening-led reading needs aligned permission and entry family, with anchors blocked mainly by hierarchy admission.",
            },
            {
                "evidence_name": "persistence_check",
                "actual": {
                    "persistence_present": persistence_present,
                    "persistence_trade_date": persistence_summary.get("persistence_trade_date"),
                },
                "reading": "If the checked late window does not preserve the specialist position while anchors churn out, the lane should not be called persistence-led.",
            },
        ]
        interpretation = [
            "The first v4 lane should only upgrade the carry reading if it contributes more than another clean opening case.",
            "The current 601919 evidence shows a specialist-only opening edge with aligned permission and entry family, but no clean persistence edge in the checked late window.",
            "So the correct current posture is to treat the first v4 lane as opening-led and keep the second lane closed until a later lane changes the carry-row-diversity reading.",
        ]
        return MarketV4Q2FirstLaneAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_market_v4_q2_first_lane_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MarketV4Q2FirstLaneAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
