from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v127g_commercial_aerospace_primary_reference_attribution_v1 import (
    V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer,
    _load_csv,
)
from a_share_quant.strategy.v127o_commercial_aerospace_new_primary_attribution_v1 import (
    V127OCommercialAerospaceNewPrimaryAttributionAnalyzer,
)
from a_share_quant.strategy.v127m_commercial_aerospace_phase_conditioned_drag_veto_audit_v1 import (
    _VetoPolicy,
)


@dataclass(slots=True)
class V127QCommercialAerospaceNewPrimaryDrawdownWindowAttributionReport:
    summary: dict[str, Any]
    window_rows: list[dict[str, Any]]
    symbol_window_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "window_rows": self.window_rows,
            "symbol_window_rows": self.symbol_window_rows,
            "interpretation": self.interpretation,
        }


class V127QCommercialAerospaceNewPrimaryDrawdownWindowAttributionAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.helper = V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer(repo_root)
        self.v127o_analyzer = V127OCommercialAerospaceNewPrimaryAttributionAnalyzer(repo_root)
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"

    @staticmethod
    def _position_state_by_date(order_rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
        by_date = sorted({row["execution_trade_date"] for row in order_rows})
        rows_by_date: dict[str, list[dict[str, Any]]] = {}
        for row in order_rows:
            rows_by_date.setdefault(row["execution_trade_date"], []).append(row)
        positions: dict[str, int] = {}
        states: dict[str, dict[str, int]] = {}
        for trade_date in by_date:
            for row in sorted(rows_by_date[trade_date], key=lambda item: (item["symbol"], item["action"])):
                quantity = int(row["quantity"])
                if row["action"] == "open":
                    positions[row["symbol"]] = positions.get(row["symbol"], 0) + quantity
                else:
                    remaining = positions.get(row["symbol"], 0) - quantity
                    if remaining > 0:
                        positions[row["symbol"]] = remaining
                    else:
                        positions.pop(row["symbol"], None)
            states[trade_date] = dict(positions)
        return states

    @staticmethod
    def _state_on_or_before(states: dict[str, dict[str, int]], trade_date: str) -> dict[str, int]:
        eligible_dates = [date for date in states if date <= trade_date]
        if not eligible_dates:
            return {}
        return states[max(eligible_dates)]

    def analyze(self) -> V127QCommercialAerospaceNewPrimaryDrawdownWindowAttributionReport:
        payload = self.v127o_analyzer.analyze()
        old_primary = self.v127o_analyzer._simulate_with_policy(
            policy=_VetoPolicy("broad_half_reference", set(), set(), set())
        )
        new_primary = self.v127o_analyzer._simulate_with_policy(
            policy=_VetoPolicy("veto_drag_trio_impulse_only", set(), set(), set(self.v127o_analyzer._drag_symbols()[:3]))
        )
        # Recreate policies without relying on hidden internals.
        if old_primary["variant"] != "broad_half_reference" or new_primary["variant"] != "veto_drag_trio_impulse_only":
            raise AssertionError("Unexpected variant naming in v127q")

        daily_map = {(row["symbol"], row["trade_date"]): row for row in _load_csv(self.daily_path)}
        new_episodes = self.helper._drawdown_episodes(new_primary["daily_rows"])[:3]

        old_states = self._position_state_by_date(old_primary["order_rows"])
        new_states = self._position_state_by_date(new_primary["order_rows"])

        window_rows: list[dict[str, Any]] = []
        symbol_window_rows: list[dict[str, Any]] = []
        for rank, episode in enumerate(new_episodes, start=1):
            peak_date = episode["peak_trade_date"]
            trough_date = episode["trough_trade_date"]
            window_rows.append(
                {
                    "rank": rank,
                    "peak_trade_date": peak_date,
                    "trough_trade_date": trough_date,
                    "new_primary_drawdown": episode["drawdown"],
                    "old_primary_drawdown": self.helper._window_drawdown(old_primary["daily_rows"], peak_date, trough_date),
                    "new_primary_reduce_count": self.helper._reduce_orders_in_window(new_primary["order_rows"], peak_date, trough_date)[0],
                    "new_primary_reduce_notional": self.helper._reduce_orders_in_window(new_primary["order_rows"], peak_date, trough_date)[1],
                    "old_primary_reduce_count": self.helper._reduce_orders_in_window(old_primary["order_rows"], peak_date, trough_date)[0],
                    "old_primary_reduce_notional": self.helper._reduce_orders_in_window(old_primary["order_rows"], peak_date, trough_date)[1],
                }
            )
            old_state = self._state_on_or_before(old_states, peak_date)
            new_state = self._state_on_or_before(new_states, peak_date)
            symbols = sorted(set(old_state) | set(new_state))
            for symbol in symbols:
                peak_close = float(daily_map[(symbol, peak_date)]["close"])
                trough_close = float(daily_map[(symbol, trough_date)]["close"])
                old_qty = old_state.get(symbol, 0)
                new_qty = new_state.get(symbol, 0)
                old_reduce_rows = [
                    row for row in old_primary["order_rows"]
                    if row["action"] == "reduce" and row["symbol"] == symbol and peak_date <= row["execution_trade_date"] <= trough_date
                ]
                new_reduce_rows = [
                    row for row in new_primary["order_rows"]
                    if row["action"] == "reduce" and row["symbol"] == symbol and peak_date <= row["execution_trade_date"] <= trough_date
                ]
                symbol_window_rows.append(
                    {
                        "rank": rank,
                        "symbol": symbol,
                        "peak_trade_date": peak_date,
                        "trough_trade_date": trough_date,
                        "old_peak_quantity": old_qty,
                        "new_peak_quantity": new_qty,
                        "old_peak_market_value": round(old_qty * peak_close, 4),
                        "new_peak_market_value": round(new_qty * peak_close, 4),
                        "old_mark_to_market_pressure": round(old_qty * (trough_close - peak_close), 4),
                        "new_mark_to_market_pressure": round(new_qty * (trough_close - peak_close), 4),
                        "old_reduce_count": len(old_reduce_rows),
                        "new_reduce_count": len(new_reduce_rows),
                        "old_reduce_notional": round(sum(float(row["notional"]) for row in old_reduce_rows), 4),
                        "new_reduce_notional": round(sum(float(row["notional"]) for row in new_reduce_rows), 4),
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v127q_commercial_aerospace_new_primary_drawdown_window_attribution_v1",
            "old_primary_variant": payload.summary["old_primary_variant"],
            "new_primary_variant": payload.summary["new_primary_variant"],
            "equity_delta": payload.summary["equity_delta"],
            "drawdown_delta": payload.summary["drawdown_delta"],
            "largest_new_primary_drawdown_window": f"{new_episodes[0]['peak_trade_date']}->{new_episodes[0]['trough_trade_date']}" if new_episodes else "",
        }
        interpretation = [
            "V1.27Q attributes the top drawdown windows of the new primary reference against the old broad-half reference.",
            "The point is to see whether the selective veto genuinely improves the worst windows or only shifts pressure to a new symbol set.",
        ]
        return V127QCommercialAerospaceNewPrimaryDrawdownWindowAttributionReport(
            summary=summary,
            window_rows=window_rows,
            symbol_window_rows=symbol_window_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127QCommercialAerospaceNewPrimaryDrawdownWindowAttributionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127QCommercialAerospaceNewPrimaryDrawdownWindowAttributionAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127q_commercial_aerospace_new_primary_drawdown_window_attribution_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
