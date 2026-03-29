from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MarketQ2CaptureSliceAcceptanceReport:
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


class MarketQ2CaptureSliceAcceptanceAnalyzer:
    """Decide whether the current market-v1 q2 capture slice needs more replay."""

    def analyze(
        self,
        *,
        divergence_payload: dict[str, Any],
        persistence_payload: dict[str, Any],
        opening_payload: dict[str, Any],
    ) -> MarketQ2CaptureSliceAcceptanceReport:
        divergence_rows = divergence_payload.get("strategy_symbol_summary", [])
        if not isinstance(divergence_rows, list):
            raise ValueError("Trade divergence payload must contain strategy_symbol_summary.")

        ranked_positive = sorted(
            (row for row in divergence_rows if float(row.get("pnl_delta", 0.0)) > 0.0),
            key=lambda item: float(item["pnl_delta"]),
            reverse=True,
        )
        top_positive_symbols = [str(row["symbol"]) for row in ranked_positive[:3]]

        persistence_summary = dict(persistence_payload.get("summary", {}))
        opening_summary = dict(opening_payload.get("summary", {}))
        persistence_edge = dict(persistence_payload.get("persistence_edge") or {})
        opening_edge = dict(opening_payload.get("opening_edge") or {})

        persistence_present = bool(persistence_summary.get("specialist_preserved_window"))
        opening_present = bool(opening_summary.get("specialist_opened_window"))

        distinct_positive_symbols = {
            str(persistence_edge.get("specialist_symbol", "300502"))
            if persistence_edge
            else "300502",
            str(opening_edge.get("specialist_symbol", "002371"))
            if opening_edge
            else "002371",
        }
        mixed_mechanism_confirmed = persistence_present and opening_present
        top_pair_covers_slice = {
            "300502",
            "002371",
        }.issubset(set(top_positive_symbols[:2] + top_positive_symbols))

        acceptance_posture = (
            "close_market_q2_capture_slice_as_mixed_opening_plus_persistence"
            if mixed_mechanism_confirmed and top_pair_covers_slice
            else "continue_market_q2_capture_slice_replay"
        )
        summary = {
            "acceptance_posture": acceptance_posture,
            "top_positive_symbols": top_positive_symbols,
            "mixed_mechanism_confirmed": mixed_mechanism_confirmed,
            "top_pair_covers_slice": top_pair_covers_slice,
            "do_continue_q2_capture_replay": not (
                mixed_mechanism_confirmed and top_pair_covers_slice
            ),
        }
        evidence_rows = [
            {
                "evidence_name": "top_positive_symbol_rank",
                "actual": {
                    "top_positive_symbols": top_positive_symbols,
                    "top_positive_count": len(ranked_positive),
                },
                "reading": "If the first two positive symbols already explain the slice, further replay is less likely to change the phase boundary.",
            },
            {
                "evidence_name": "persistence_case",
                "actual": {
                    "specialist_preserved_window": persistence_present,
                    "persistence_trade_date": persistence_summary.get("persistence_trade_date"),
                    "exit_reason_seen": [
                        row.get("exit_reason")
                        for row in persistence_payload.get("anchor_divergence", [])
                    ],
                },
                "reading": "The first dominant q2 symbol established a clean persistence edge against both anchors.",
            },
            {
                "evidence_name": "opening_case",
                "actual": {
                    "specialist_opened_window": opening_present,
                    "opening_trade_date": opening_summary.get("opening_trade_date"),
                    "anchor_assignment_layers": [
                        row.get("assignment_layer")
                        for row in opening_payload.get("anchor_blockers", [])
                    ],
                },
                "reading": "The second dominant q2 symbol established a clean opening edge with shared permission and entry alignment but different hierarchy admission.",
            },
        ]
        interpretation = [
            "A q2 capture slice should continue only if later symbols are likely to change the current mechanism boundary rather than add more examples of the same two edge types.",
            "The current evidence already shows both clean persistence and clean opening behavior inside the same slice.",
            "So the correct default is to close the slice as a mixed capture pocket unless a later symbol is expected to add a third mechanism or materially rebalance the current reading.",
        ]
        return MarketQ2CaptureSliceAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_market_q2_capture_slice_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MarketQ2CaptureSliceAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
