from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MarketV2RefreshQ1DrawdownSliceAcceptanceReport:
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


class MarketV2RefreshQ1DrawdownSliceAcceptanceAnalyzer:
    """Decide whether the v2-refresh q1/C drawdown slice merits more replay."""

    def analyze(
        self,
        *,
        divergence_payload: dict[str, Any],
        top_mechanism_payload: dict[str, Any],
        second_mechanism_payload: dict[str, Any],
    ) -> MarketV2RefreshQ1DrawdownSliceAcceptanceReport:
        divergence_rows = divergence_payload.get("strategy_symbol_summary", [])
        if not isinstance(divergence_rows, list):
            raise ValueError("Trade divergence payload must contain strategy_symbol_summary.")

        ranked_positive = sorted(
            (row for row in divergence_rows if float(row.get("pnl_delta", 0.0)) > 0.0),
            key=lambda item: float(item["pnl_delta"]),
            reverse=True,
        )
        top_positive_symbols = [str(row["symbol"]) for row in ranked_positive[:3]]

        top_rows = top_mechanism_payload.get("mechanism_rows", [])
        second_rows = second_mechanism_payload.get("mechanism_rows", [])
        if not isinstance(top_rows, list) or not isinstance(second_rows, list):
            raise ValueError("Mechanism payloads must contain mechanism_rows.")

        top_negative_types = {
            str(row.get("mechanism_type"))
            for row in top_rows
            if str(row.get("cycle_sign")) == "negative"
        }
        second_positive_types = {
            str(row.get("mechanism_type"))
            for row in second_rows
            if str(row.get("cycle_sign")) == "positive"
        }

        top_driver_matches_read = len(top_positive_symbols) >= 2 and top_positive_symbols[:2] == [
            "002415",
            "603019",
        ]
        clean_avoidance_present = top_negative_types == {"entry_suppression_avoidance"}
        positive_fragmentation_present = "other_worse_loss_shift" in second_positive_types

        close_slice = (
            top_driver_matches_read
            and clean_avoidance_present
            and positive_fragmentation_present
        )
        acceptance_posture = (
            "close_market_v2_refresh_q1_drawdown_slice_as_avoidance_plus_positive_fragmentation"
            if close_slice
            else "continue_market_v2_refresh_q1_drawdown_replay"
        )
        summary = {
            "acceptance_posture": acceptance_posture,
            "top_positive_symbols": top_positive_symbols,
            "top_driver_matches_read": top_driver_matches_read,
            "clean_avoidance_present": clean_avoidance_present,
            "positive_fragmentation_present": positive_fragmentation_present,
            "do_continue_q1_drawdown_replay": not close_slice,
        }
        evidence_rows = [
            {
                "evidence_name": "top_positive_symbol_rank",
                "actual": {
                    "top_positive_symbols": top_positive_symbols,
                    "top_positive_count": len(ranked_positive),
                },
                "reading": "A q1 drawdown slice only deserves more replay if later symbols are likely to overturn the current two-driver read.",
            },
            {
                "evidence_name": "top_driver_mechanism_shape",
                "actual": {
                    "negative_mechanism_types": sorted(top_negative_types),
                    "summary": top_mechanism_payload.get("summary", {}),
                },
                "reading": "The leading q1 symbol should first be tested as a clean drawdown-avoidance read.",
            },
            {
                "evidence_name": "second_driver_fragmentation_shape",
                "actual": {
                    "positive_mechanism_types": sorted(second_positive_types),
                    "summary": second_mechanism_payload.get("summary", {}),
                },
                "reading": "A positive fragmentation row weakens the purity of the slice, turning it into a mixed read rather than a clean drawdown-family frontier.",
            },
        ]
        interpretation = [
            "A q1 drawdown slice should stop once its top driver is a clean avoidance case and the second driver is a positive-fragmentation case.",
            "That mix is informative and worth keeping, but it does not justify a broader replay queue inside the same slice.",
            "So the correct default is to close q1 here unless a later symbol is likely to overturn the current mixed read.",
        ]
        return MarketV2RefreshQ1DrawdownSliceAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_market_v2_refresh_q1_drawdown_slice_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MarketV2RefreshQ1DrawdownSliceAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
