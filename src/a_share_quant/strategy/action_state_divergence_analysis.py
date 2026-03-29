from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ACTION_STATE_TYPES = {"emitted_actions", "position_qty", "pending_buy", "pending_sell"}


@dataclass(slots=True)
class ActionStateDivergenceReport:
    summary: dict[str, Any]
    symbol_summaries: list[dict[str, Any]]
    trigger_date_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_summaries": self.symbol_summaries,
            "trigger_date_rows": self.trigger_date_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class ActionStateDivergenceAnalyzer:
    """Identify which repeated shift dates actually cross the action-state boundary."""

    def analyze(self, *, case_payloads: list[dict[str, Any]]) -> ActionStateDivergenceReport:
        symbol_summaries: list[dict[str, Any]] = []
        trigger_date_rows: list[dict[str, Any]] = []
        for case in case_payloads:
            symbol_summary, symbol_rows = self._analyze_case(case)
            symbol_summaries.append(symbol_summary)
            trigger_date_rows.extend(symbol_rows)

        triggered_symbols = [row["symbol"] for row in symbol_summaries if row["triggered_date_count"] > 0]
        summary = {
            "case_count": len(symbol_summaries),
            "triggered_symbol_count": len(triggered_symbols),
            "triggered_symbols": triggered_symbols,
            "core_rule": (
                "A repeated split becomes action-state relevant only when it changes emitted actions "
                "or active position state on a repeated shift date."
            ),
        }
        interpretation = [
            "Permission or assignment splits are necessary but not sufficient; the next useful boundary is whether they also change emitted actions or position state.",
            "Action-state trigger dates are the best candidates for explaining real trade-path divergence.",
            "Symbols with repeated structural splits but zero action-state trigger dates should be treated as latent cases, not immediate repair targets.",
        ]
        return ActionStateDivergenceReport(
            summary=summary,
            symbol_summaries=symbol_summaries,
            trigger_date_rows=trigger_date_rows,
            interpretation=interpretation,
        )

    def _analyze_case(self, case: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        symbol = str(case["symbol"])
        path_payload = case["path_payload"]
        repeated_shift_dates = {
            str(item["trade_date"]) for item in path_payload.get("repeated_shift_dates", [])
        }
        detailed_shifts = [
            item
            for item in path_payload.get("detailed_shifts", [])
            if str(item.get("trade_date")) in repeated_shift_dates
        ]

        trigger_rows: list[dict[str, Any]] = []
        for item in detailed_shifts:
            difference_types = list(item.get("difference_types", []))
            action_state_types = [diff for diff in difference_types if diff in ACTION_STATE_TYPES]
            if not action_state_types:
                continue
            trigger_rows.append(
                {
                    "symbol": symbol,
                    "strategy_name": str(item.get("strategy_name")),
                    "trade_date": str(item.get("trade_date")),
                    "action_state_types": action_state_types,
                    "difference_types": difference_types,
                    "incumbent_emitted_actions": item.get("incumbent_emitted_actions", []),
                    "challenger_emitted_actions": item.get("challenger_emitted_actions", []),
                    "incumbent_position_qty": int(item.get("incumbent_position_qty", 0)),
                    "challenger_position_qty": int(item.get("challenger_position_qty", 0)),
                }
            )

        unique_trigger_dates = sorted({row["trade_date"] for row in trigger_rows})
        symbol_summary = {
            "symbol": symbol,
            "repeated_shift_date_count": len(repeated_shift_dates),
            "triggered_date_count": len(unique_trigger_dates),
            "triggered_dates": unique_trigger_dates,
            "has_action_state_trigger": bool(unique_trigger_dates),
            "trigger_strategy_count": len({row["strategy_name"] for row in trigger_rows}),
        }
        return symbol_summary, trigger_rows


def write_action_state_divergence_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: ActionStateDivergenceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
