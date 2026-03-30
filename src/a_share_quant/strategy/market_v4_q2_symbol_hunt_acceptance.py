from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MarketV4Q2SymbolHuntAcceptanceReport:
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


class MarketV4Q2SymbolHuntAcceptanceAnalyzer:
    """Decide whether one v4 symbol advances the carry-row hunt or should be closed."""

    def analyze(
        self,
        *,
        target_symbol: str,
        excluded_symbols: list[str] | None,
        hunting_strategy_payload: dict[str, Any],
        divergence_payload: dict[str, Any],
        opening_payload: dict[str, Any],
        persistence_payload: dict[str, Any],
    ) -> MarketV4Q2SymbolHuntAcceptanceReport:
        excluded = {target_symbol, *(excluded_symbols or [])}
        hunt_rows = list(hunting_strategy_payload.get("hunt_rows", []))
        target_hunt_row = next(
            (row for row in hunt_rows if str(row.get("symbol", "")) == target_symbol),
            None,
        )
        if target_hunt_row is None:
            raise ValueError(f"Target symbol {target_symbol} is not present in the hunt strategy report.")

        divergence_rows = list(divergence_payload.get("strategy_symbol_summary", []))
        target_divergence_row = next(
            (row for row in divergence_rows if str(row.get("symbol", "")) == target_symbol),
            None,
        )
        if target_divergence_row is None:
            raise ValueError(f"Target symbol {target_symbol} is not present in the divergence report.")

        target_delta = float(target_divergence_row.get("pnl_delta", 0.0))
        incumbent_trade_count = int(target_divergence_row.get("incumbent_trade_count", 0))
        challenger_trade_count = int(target_divergence_row.get("challenger_trade_count", 0))
        identical_trade_count_signature = incumbent_trade_count == challenger_trade_count

        opening_summary = dict(opening_payload.get("summary", {}))
        persistence_summary = dict(persistence_payload.get("summary", {}))
        opening_present = bool(opening_summary.get("specialist_opened_window"))
        persistence_present = bool(persistence_summary.get("specialist_preserved_window"))
        lane_changes_carry_reading = bool(opening_present or persistence_present or abs(target_delta) > 1e-9)

        next_symbol = ""
        for row in hunt_rows:
            if str(row.get("symbol", "")) in excluded:
                continue
            if str(row.get("hunt_posture", "")) == "hunt_next":
                next_symbol = str(row.get("symbol", ""))
                break

        if not lane_changes_carry_reading:
            acceptance_posture = "close_market_v4_q2_symbol_hunt_as_no_active_structural_lane"
        elif opening_present and not persistence_present:
            acceptance_posture = "close_market_v4_q2_symbol_hunt_as_opening_led_not_carry_breakthrough"
        else:
            acceptance_posture = "continue_market_v4_q2_symbol_hunt_structural_check"

        summary = {
            "acceptance_posture": acceptance_posture,
            "target_symbol": target_symbol,
            "target_row_diversity": str(target_hunt_row.get("target_row_diversity", "")),
            "target_pnl_delta": target_delta,
            "opening_present": opening_present,
            "persistence_present": persistence_present,
            "identical_trade_count_signature": identical_trade_count_signature,
            "lane_changes_carry_reading": lane_changes_carry_reading,
            "do_continue_current_symbol_now": False,
            "do_continue_hunt_with_next_symbol": True,
            "recommended_next_symbol": next_symbol,
        }
        evidence_rows = [
            {
                "evidence_name": "hunt_target",
                "actual": {
                    "target_symbol": target_symbol,
                    "target_row_diversity": target_hunt_row.get("target_row_diversity"),
                    "carry_row_hypothesis": target_hunt_row.get("carry_row_hypothesis"),
                },
                "reading": "A v4 symbol should be judged against the specific row-diversity gap it was selected to probe.",
            },
            {
                "evidence_name": "divergence_signature",
                "actual": {
                    "target_pnl_delta": target_delta,
                    "incumbent_trade_count": incumbent_trade_count,
                    "challenger_trade_count": challenger_trade_count,
                    "identical_trade_count_signature": identical_trade_count_signature,
                },
                "reading": "If the symbol shows zero pnl delta and no trade-count divergence, the hunt should assume no active structural lane until a replay proves otherwise.",
            },
            {
                "evidence_name": "window_checks",
                "actual": {
                    "opening_present": opening_present,
                    "opening_trade_date": opening_summary.get("opening_trade_date"),
                    "persistence_present": persistence_present,
                    "persistence_trade_date": persistence_summary.get("persistence_trade_date"),
                },
                "reading": "The hunt only stays open when opening or persistence analysis surfaces an actual specialist-owned window.",
            },
        ]
        interpretation = [
            "A carry-row hunt should not be forced just because a symbol was selected for row-diversity coverage.",
            "If the selected symbol shows no pnl divergence and no specialist-owned opening or persistence window, the correct posture is to close that hunt and move to the next symbol.",
            "This keeps v4 focused on one symbol at a time without relabeling inactive lanes as carry evidence.",
        ]
        return MarketV4Q2SymbolHuntAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_market_v4_q2_symbol_hunt_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MarketV4Q2SymbolHuntAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
