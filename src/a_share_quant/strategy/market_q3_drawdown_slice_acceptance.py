from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MarketQ3DrawdownSliceAcceptanceReport:
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


class MarketQ3DrawdownSliceAcceptanceAnalyzer:
    """Decide whether the current market-v1 q3 drawdown slice needs more replay."""

    def analyze(
        self,
        *,
        divergence_payloads: list[dict[str, Any]],
        consistency_payload: dict[str, Any],
    ) -> MarketQ3DrawdownSliceAcceptanceReport:
        top_positive_symbols: list[str] = []
        per_strategy_rows: list[dict[str, Any]] = []

        for payload in divergence_payloads:
            summary = dict(payload.get("summary", {}))
            strategy_name = str(summary.get("strategy_name"))
            rows = payload.get("strategy_symbol_summary", [])
            if not isinstance(rows, list):
                raise ValueError("Trade divergence payload must contain strategy_symbol_summary.")
            ranked_positive = sorted(
                (row for row in rows if float(row.get("pnl_delta", 0.0)) > 0.0),
                key=lambda item: float(item["pnl_delta"]),
                reverse=True,
            )
            top_symbol = str(ranked_positive[0]["symbol"]) if ranked_positive else ""
            top_positive_symbols.append(top_symbol)
            per_strategy_rows.append(
                {
                    "strategy_name": strategy_name,
                    "top_positive_symbol": top_symbol,
                    "top_positive_pnl_delta": float(ranked_positive[0]["pnl_delta"]) if ranked_positive else 0.0,
                    "positive_symbol_count": len(ranked_positive),
                }
            )

        consistency_summary = dict(consistency_payload.get("summary", {}))
        identical_negative_cycle_map = bool(consistency_summary.get("identical_negative_cycle_map"))
        shared_negative_mechanism_count = int(consistency_summary.get("shared_negative_mechanism_count", 0))
        same_top_driver = len(set(symbol for symbol in top_positive_symbols if symbol)) == 1 and bool(top_positive_symbols)
        top_driver = top_positive_symbols[0] if same_top_driver else ""

        acceptance_posture = (
            "close_market_q3_drawdown_slice_as_cross_strategy_baseline_style_reuse"
            if identical_negative_cycle_map and shared_negative_mechanism_count >= 3 and same_top_driver
            else "continue_market_q3_drawdown_slice_replay"
        )
        summary = {
            "acceptance_posture": acceptance_posture,
            "top_positive_symbols_by_strategy": top_positive_symbols,
            "shared_top_driver": top_driver,
            "same_top_driver": same_top_driver,
            "identical_negative_cycle_map": identical_negative_cycle_map,
            "shared_negative_mechanism_count": shared_negative_mechanism_count,
            "do_continue_q3_drawdown_replay": not (
                identical_negative_cycle_map and shared_negative_mechanism_count >= 3 and same_top_driver
            ),
        }
        evidence_rows = [
            {
                "evidence_name": "top_driver_alignment",
                "actual": {
                    "per_strategy_rows": per_strategy_rows,
                    "shared_top_driver": top_driver,
                },
                "reading": "If the same symbol dominates the positive drawdown delta in both B and C, the slice is more likely to be structurally coherent rather than strategy-specific noise.",
            },
            {
                "evidence_name": "cross_strategy_cycle_consistency",
                "actual": {
                    "identical_negative_cycle_map": identical_negative_cycle_map,
                    "shared_negative_mechanism_count": shared_negative_mechanism_count,
                    "shared_mechanisms": consistency_payload.get("shared_mechanisms", []),
                },
                "reading": "An identical negative-cycle map means later replay is unlikely to change the family boundary; it will mostly add more examples of the same drawdown template.",
            },
        ]
        interpretation = [
            "A q3 drawdown slice should continue only if a later symbol is likely to break the current cross-strategy mechanism map.",
            "If both B and C are driven by the same symbol and share the same negative-cycle signatures, the correct default is to close the slice as cross-strategy stable.",
            "Under that condition, new replay effort should move to other slices or other family frontiers instead of re-explaining the same q3 pocket.",
        ]
        return MarketQ3DrawdownSliceAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_market_q3_drawdown_slice_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MarketQ3DrawdownSliceAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
