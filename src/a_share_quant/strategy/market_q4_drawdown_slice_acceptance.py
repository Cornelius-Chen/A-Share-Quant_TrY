from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MarketQ4DrawdownSliceAcceptanceReport:
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


class MarketQ4DrawdownSliceAcceptanceAnalyzer:
    """Decide whether the current market-v1 q4 drawdown slice needs more replay."""

    def analyze(
        self,
        *,
        divergence_payload: dict[str, Any],
        first_mechanism_payload: dict[str, Any],
        second_mechanism_payload: dict[str, Any],
    ) -> MarketQ4DrawdownSliceAcceptanceReport:
        divergence_rows = divergence_payload.get("strategy_symbol_summary", [])
        if not isinstance(divergence_rows, list):
            raise ValueError("Trade divergence payload must contain strategy_symbol_summary.")

        ranked_positive = sorted(
            (row for row in divergence_rows if float(row.get("pnl_delta", 0.0)) > 0.0),
            key=lambda item: float(item["pnl_delta"]),
            reverse=True,
        )
        top_positive_symbols = [str(row["symbol"]) for row in ranked_positive[:3]]

        first_rows = list(first_mechanism_payload.get("mechanism_rows", []))
        second_rows = list(second_mechanism_payload.get("mechanism_rows", []))
        first_negative_types = {
            str(row.get("mechanism_type"))
            for row in first_rows
            if str(row.get("cycle_sign")) == "negative"
        }
        second_negative_types = {
            str(row.get("mechanism_type"))
            for row in second_rows
            if str(row.get("cycle_sign")) == "negative"
        }

        first_symbol_is_clean_avoidance = first_negative_types == {"entry_suppression_avoidance"}
        second_symbol_expands_beyond_avoidance = bool(
            second_negative_types - {"entry_suppression_avoidance"}
        )
        top_pair_covers_slice = {"002371", "000977"}.issubset(set(top_positive_symbols))

        acceptance_posture = (
            "close_market_q4_drawdown_slice_as_avoidance_plus_reduced_loss_mix"
            if first_symbol_is_clean_avoidance and second_symbol_expands_beyond_avoidance and top_pair_covers_slice
            else "continue_market_q4_drawdown_replay"
        )
        summary = {
            "acceptance_posture": acceptance_posture,
            "top_positive_symbols": top_positive_symbols,
            "first_symbol_is_clean_avoidance": first_symbol_is_clean_avoidance,
            "second_symbol_expands_beyond_avoidance": second_symbol_expands_beyond_avoidance,
            "top_pair_covers_slice": top_pair_covers_slice,
            "do_continue_q4_drawdown_replay": not (
                first_symbol_is_clean_avoidance and second_symbol_expands_beyond_avoidance and top_pair_covers_slice
            ),
        }
        evidence_rows = [
            {
                "evidence_name": "top_positive_symbol_rank",
                "actual": {
                    "top_positive_symbols": top_positive_symbols,
                    "top_positive_count": len(ranked_positive),
                },
                "reading": "If the first two positive symbols already split into different mechanism shapes, further replay is less likely to change the slice-level boundary.",
            },
            {
                "evidence_name": "first_symbol_mechanism",
                "actual": {
                    "mechanism_types": sorted(first_negative_types),
                    "summary": first_mechanism_payload.get("summary", {}),
                },
                "reading": "The first q4 symbol should be read as a pure avoidance probe.",
            },
            {
                "evidence_name": "second_symbol_mechanism",
                "actual": {
                    "mechanism_types": sorted(second_negative_types),
                    "summary": second_mechanism_payload.get("summary", {}),
                },
                "reading": "The second q4 symbol should widen q4 beyond pure avoidance if it carries reduced-loss structure.",
            },
        ]
        interpretation = [
            "A q4 drawdown slice should continue only if later symbols are likely to break the current two-part reading.",
            "If one top symbol is pure avoidance and the next top symbol adds reduced-loss structure, q4 has already changed from a single-mechanism read into a mixed drawdown slice.",
            "Under that condition, further replay should stop unless a later symbol is expected to add a genuinely new family rather than one more example of the same mixed slice.",
        ]
        return MarketQ4DrawdownSliceAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_market_q4_drawdown_slice_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MarketQ4DrawdownSliceAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
