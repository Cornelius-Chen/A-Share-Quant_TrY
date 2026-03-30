from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MarketV2SeedQ3DrawdownSliceAcceptanceReport:
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


class MarketV2SeedQ3DrawdownSliceAcceptanceAnalyzer:
    """Decide whether the v2-seed q3/C drawdown slice merits more replay."""

    def analyze(
        self,
        *,
        divergence_payload: dict[str, Any],
        mechanism_payload: dict[str, Any],
    ) -> MarketV2SeedQ3DrawdownSliceAcceptanceReport:
        divergence_rows = divergence_payload.get("strategy_symbol_summary", [])
        if not isinstance(divergence_rows, list):
            raise ValueError("Trade divergence payload must contain strategy_symbol_summary.")

        ranked_positive = sorted(
            (row for row in divergence_rows if float(row.get("pnl_delta", 0.0)) > 0.0),
            key=lambda item: float(item["pnl_delta"]),
            reverse=True,
        )
        top_positive_symbols = [str(row["symbol"]) for row in ranked_positive[:3]]
        dominant_symbol = top_positive_symbols[0] if top_positive_symbols else None

        mechanism_rows = mechanism_payload.get("mechanism_rows", [])
        if not isinstance(mechanism_rows, list):
            raise ValueError("Mechanism payload must contain mechanism_rows.")

        negative_mechanism_types = {
            str(row.get("mechanism_type"))
            for row in mechanism_rows
            if str(row.get("cycle_sign")) == "negative"
        }
        positive_mechanism_types = {
            str(row.get("mechanism_type"))
            for row in mechanism_rows
            if str(row.get("cycle_sign")) == "positive"
        }

        clean_avoidance_present = negative_mechanism_types == {"entry_suppression_avoidance"}
        opportunity_cost_present = "entry_suppression_opportunity_cost" in positive_mechanism_types
        top_driver_matches_read = dominant_symbol == "603986"

        close_slice = clean_avoidance_present and opportunity_cost_present and top_driver_matches_read
        acceptance_posture = (
            "close_market_v2_seed_q3_drawdown_slice_as_avoidance_plus_opportunity_cost"
            if close_slice
            else "continue_market_v2_seed_q3_drawdown_replay"
        )
        summary = {
            "acceptance_posture": acceptance_posture,
            "top_positive_symbols": top_positive_symbols,
            "top_driver_matches_read": top_driver_matches_read,
            "clean_avoidance_present": clean_avoidance_present,
            "opportunity_cost_present": opportunity_cost_present,
            "do_continue_q3_drawdown_replay": not close_slice,
        }
        evidence_rows = [
            {
                "evidence_name": "top_positive_symbol_rank",
                "actual": {
                    "top_positive_symbols": top_positive_symbols,
                    "top_positive_count": len(ranked_positive),
                },
                "reading": "A q3 drawdown slice only deserves more replay if later symbols are likely to overturn the dominant symbol's mechanism mix.",
            },
            {
                "evidence_name": "negative_mechanism_shape",
                "actual": {
                    "negative_mechanism_types": sorted(negative_mechanism_types),
                    "summary": mechanism_payload.get("summary", {}),
                },
                "reading": "The dominant q3 symbol should first be tested as a clean drawdown-avoidance read.",
            },
            {
                "evidence_name": "positive_opportunity_cost_shape",
                "actual": {
                    "positive_mechanism_types": sorted(positive_mechanism_types),
                },
                "reading": "A positive opportunity-cost row weakens the purity of the q3 drawdown read, turning it into a mixed slice instead of a clean family frontier.",
            },
        ]
        interpretation = [
            "A q3 drawdown slice should stop once the dominant symbol is clearly read as avoidance plus opportunity cost.",
            "That mix is real and useful, but it is not the same as discovering a clean new drawdown family.",
            "So the correct default is to close q3 here unless a later symbol is expected to overturn the current mixed read.",
        ]
        return MarketV2SeedQ3DrawdownSliceAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_market_v2_seed_q3_drawdown_slice_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MarketV2SeedQ3DrawdownSliceAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
