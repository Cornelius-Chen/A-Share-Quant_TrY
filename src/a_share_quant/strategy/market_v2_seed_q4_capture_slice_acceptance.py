from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MarketV2SeedQ4CaptureSliceAcceptanceReport:
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


class MarketV2SeedQ4CaptureSliceAcceptanceAnalyzer:
    """Decide whether the v2-seed q4/C capture slice merits more replay."""

    def analyze(
        self,
        *,
        divergence_payload: dict[str, Any],
        timeline_payload: dict[str, Any],
        opening_payload: dict[str, Any],
        slice_start: str,
    ) -> MarketV2SeedQ4CaptureSliceAcceptanceReport:
        divergence_rows = divergence_payload.get("strategy_symbol_summary", [])
        if not isinstance(divergence_rows, list):
            raise ValueError("Trade divergence payload must contain strategy_symbol_summary.")

        ranked_positive = sorted(
            (row for row in divergence_rows if float(row.get("pnl_delta", 0.0)) > 0.0),
            key=lambda item: float(item["pnl_delta"]),
            reverse=True,
        )
        top_positive_symbols = [str(row["symbol"]) for row in ranked_positive[:3]]
        top_symbol = str(top_positive_symbols[0]) if top_positive_symbols else None

        opening_summary = dict(opening_payload.get("summary", {}))
        opening_edge = dict(opening_payload.get("opening_edge") or {})
        specialist_opened_window = bool(opening_summary.get("specialist_opened_window"))

        candidate_records = timeline_payload.get("candidate_records", [])
        if not isinstance(candidate_records, list):
            raise ValueError("Timeline payload must contain candidate_records.")
        challenger_record = next(
            (
                record
                for record in candidate_records
                if str(record.get("candidate_name")) == str(opening_summary.get("specialist_candidate"))
            ),
            None,
        )
        carry_in_positive_trade = None
        if challenger_record is not None:
            for trade in challenger_record.get("closed_trades", []):
                entry_date = str(trade.get("entry_date"))
                exit_date = str(trade.get("exit_date"))
                pnl = float(trade.get("pnl", 0.0))
                if entry_date < slice_start <= exit_date and pnl > 0.0:
                    carry_in_positive_trade = dict(trade)
                    break

        top_symbol_matches_opening = top_symbol == str(opening_edge.get("specialist_symbol", top_symbol))
        carry_in_present = carry_in_positive_trade is not None
        mixed_mechanism_confirmed = specialist_opened_window and carry_in_present and top_symbol_matches_opening

        acceptance_posture = (
            "close_market_v2_seed_q4_capture_slice_as_opening_plus_carry"
            if mixed_mechanism_confirmed
            else "continue_market_v2_seed_q4_capture_replay"
        )
        summary = {
            "acceptance_posture": acceptance_posture,
            "top_positive_symbols": top_positive_symbols,
            "top_symbol_matches_opening": top_symbol_matches_opening,
            "specialist_opened_window": specialist_opened_window,
            "carry_in_positive_trade_present": carry_in_present,
            "do_continue_q4_capture_replay": not mixed_mechanism_confirmed,
        }
        evidence_rows = [
            {
                "evidence_name": "top_positive_symbol_rank",
                "actual": {
                    "top_positive_symbols": top_positive_symbols,
                    "top_positive_count": len(ranked_positive),
                },
                "reading": "A single dominant symbol is enough to justify one narrow replay, but not enough to justify a broad queue restart.",
            },
            {
                "evidence_name": "opening_case",
                "actual": {
                    "specialist_opened_window": specialist_opened_window,
                    "opening_trade_date": opening_summary.get("opening_trade_date"),
                    "opening_symbol": opening_edge.get("specialist_symbol", top_symbol),
                },
                "reading": "The q4/C pocket contains a real specialist-only opening edge inside the slice.",
            },
            {
                "evidence_name": "carry_in_case",
                "actual": {
                    "carry_in_positive_trade": carry_in_positive_trade,
                    "slice_start": slice_start,
                },
                "reading": "A positive carry-in trade weakens the purity of the slice-level read because part of the gain starts before q4.",
            },
        ]
        interpretation = [
            "A q4 capture slice should continue only if the dominant symbol gives a clean in-slice mechanism boundary.",
            "When the same dominant symbol contains both a clean opening edge and a positive carry-in trade, the slice is real but mixed.",
            "So the correct default is to close the slice as mixed opening-plus-carry unless a later symbol is likely to overturn that read.",
        ]
        return MarketV2SeedQ4CaptureSliceAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_market_v2_seed_q4_capture_slice_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MarketV2SeedQ4CaptureSliceAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
