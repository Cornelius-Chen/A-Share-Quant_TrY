from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from a_share_quant.strategy.v115n_cpo_intraday_strict_band_held_position_overlay_replay_v1 import (
    _costs,
    _load_daily_bars,
    _max_drawdown,
)


def parse_trade_date(value: str) -> datetime.date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


@dataclass(slots=True)
class CpoResearchTestBaselineExplainerPlotsReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "interpretation": self.interpretation,
        }


class CpoResearchTestBaselineExplainerPlotsAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _simulate_equity_curve(
        self,
        *,
        baseline_executed_orders: list[dict[str, Any]],
        overlay_orders: list[dict[str, Any]],
        baseline_day_rows: list[dict[str, Any]],
        daily_bars: dict[tuple[str, Any], dict[str, Any]],
    ) -> list[float]:
        baseline_orders_by_exec: dict[Any, list[dict[str, Any]]] = {}
        overlay_orders_by_exec: dict[Any, list[dict[str, Any]]] = {}
        for row in baseline_executed_orders:
            baseline_orders_by_exec.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)
        for row in overlay_orders:
            overlay_orders_by_exec.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)

        cash = 1_000_000.0
        positions: dict[str, int] = {}
        equity_curve: list[float] = []
        for base_day in baseline_day_rows:
            trade_date = parse_trade_date(str(base_day["trade_date"]))

            for row in baseline_orders_by_exec.get(trade_date, []):
                symbol = str(row["symbol"])
                action = str(row["action"])
                quantity = int(row["quantity"])
                execution_price = _to_float(row["execution_price"])
                notional = quantity * execution_price
                if action == "buy":
                    cash -= notional + _to_float(row["total_cost"])
                    positions[symbol] = positions.get(symbol, 0) + quantity
                else:
                    sell_qty = min(quantity, positions.get(symbol, 0))
                    proceeds = sell_qty * execution_price
                    cash += proceeds - _to_float(row["total_cost"])
                    positions[symbol] = max(0, positions.get(symbol, 0) - sell_qty)

            for row in overlay_orders_by_exec.get(trade_date, []):
                symbol = str(row["symbol"])
                quantity = int(row["quantity"])
                execution_price = _to_float(row["execution_price"])
                notional = quantity * execution_price
                cash -= notional + _to_float(row["total_cost"])
                positions[symbol] = positions.get(symbol, 0) + quantity

            equity = cash
            for symbol, qty in positions.items():
                if qty <= 0:
                    continue
                daily_row = daily_bars.get((symbol, trade_date))
                if daily_row is None:
                    continue
                equity += qty * _to_float(daily_row["close"])
            equity_curve.append(equity)
        return equity_curve

    @staticmethod
    def _baseline_action_rows(executed_orders: list[dict[str, Any]]) -> list[dict[str, Any]]:
        positions: dict[str, int] = {}
        rows: list[dict[str, Any]] = []
        ordered = sorted(
            executed_orders,
            key=lambda row: (parse_trade_date(str(row["execution_trade_date"])), str(row["symbol"]), str(row["action"])),
        )
        for row in ordered:
            exec_date = parse_trade_date(str(row["execution_trade_date"]))
            symbol = str(row["symbol"])
            action = str(row["action"])
            quantity = int(row["quantity"])
            execution_price = _to_float(row["execution_price"])
            rationale = str(row.get("rationale", ""))
            before_qty = positions.get(symbol, 0)
            if action == "buy":
                label = "open" if before_qty <= 0 else "add"
                positions[symbol] = before_qty + quantity
            else:
                label = "close" if rationale == "close_from_holding_veto" or quantity >= before_qty else "reduce"
                positions[symbol] = max(0, before_qty - quantity)
            rows.append(
                {
                    "symbol": symbol,
                    "trade_date": exec_date,
                    "price": execution_price,
                    "label": label,
                }
            )
        return rows

    @staticmethod
    def _research_add_rows(overlay_orders: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row in overlay_orders:
            rows.append(
                {
                    "symbol": str(row["symbol"]),
                    "trade_date": parse_trade_date(str(row["execution_trade_date"])),
                    "price": _to_float(row["execution_price"]),
                    "label": "research_add",
                    "components": str(row["component_names"]),
                }
            )
        return rows

    def analyze(
        self,
        *,
        v113t_payload: dict[str, Any],
        v114t_payload: dict[str, Any],
        v120e_payload: dict[str, Any],
    ) -> CpoResearchTestBaselineExplainerPlotsReport:
        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)

        baseline_day_rows = list(v114t_payload.get("replay_day_rows", []))
        baseline_executed_orders = list(v114t_payload.get("executed_order_rows", []))
        overlay_orders = list(v120e_payload.get("executed_overlay_rows", []))

        baseline_equity_curve = [_to_float(row["equity_after_close"]) for row in baseline_day_rows]
        research_equity_curve = self._simulate_equity_curve(
            baseline_executed_orders=baseline_executed_orders,
            overlay_orders=overlay_orders,
            baseline_day_rows=baseline_day_rows,
            daily_bars=daily_bars,
        )
        trade_dates = [parse_trade_date(str(row["trade_date"])) for row in baseline_day_rows]

        explainer_rows: list[dict[str, Any]] = []
        initial_capital = 1_000_000.0
        for row in baseline_executed_orders:
            action = "open"
            if str(row["action"]) == "buy" and str(row.get("rationale")) == "add_to_target_from_board_state_episode":
                action = "add"
            elif str(row["action"]) == "sell" and str(row.get("rationale")) == "reduce_from_board_state_episode":
                action = "reduce"
            elif str(row["action"]) == "sell":
                action = "close"
            explainer_rows.append(
                {
                    "lane": "baseline",
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "execution_trade_date": str(row["execution_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "action": action,
                    "reason": str(row.get("source", "")),
                    "detail": str(row.get("rationale", "")),
                    "quantity": int(row["quantity"]),
                    "execution_price": _to_float(row["execution_price"]),
                    "notional": _to_float(row["notional"]),
                    "weight_vs_initial_capital": round(_to_float(row["notional"]) / initial_capital, 6),
                }
            )
        for row in overlay_orders:
            explainer_rows.append(
                {
                    "lane": "research_test_baseline",
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "execution_trade_date": str(row["execution_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "action": "add",
                    "reason": str(row.get("component_names", "")),
                    "detail": f"component_count={row.get('component_count')}",
                    "quantity": int(row["quantity"]),
                    "execution_price": _to_float(row["execution_price"]),
                    "notional": _to_float(row["notional"]),
                    "weight_vs_initial_capital": round(_to_float(row["notional"]) / initial_capital, 6),
                }
            )
        explainer_rows = sorted(
            explainer_rows,
            key=lambda row: (row["execution_trade_date"], row["lane"], row["symbol"]),
        )

        explainer_csv = self.repo_root / "data" / "training" / "cpo_research_test_baseline_trade_explainer_v1.csv"
        explainer_csv.parent.mkdir(parents=True, exist_ok=True)
        with explainer_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(explainer_rows[0].keys()))
            writer.writeheader()
            writer.writerows(explainer_rows)

        equity_png = self.repo_root / "reports" / "analysis" / "v120f_cpo_research_test_baseline_equity_curve_v1.png"
        marker_png = self.repo_root / "reports" / "analysis" / "v120f_cpo_research_test_baseline_daily_markers_v1.png"

        plt.figure(figsize=(12, 6))
        plt.plot(trade_dates, baseline_equity_curve, label="baseline_v114t", color="#111111", linewidth=2.2)
        plt.plot(trade_dates, research_equity_curve, label="research_test_baseline", color="#1f77b4", linewidth=1.8)
        plt.title("CPO Baseline vs Research Test Baseline")
        plt.xlabel("Trade Date")
        plt.ylabel("Equity")
        plt.legend(fontsize=9)
        plt.tight_layout()
        equity_png.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(equity_png, dpi=160)
        plt.close()

        baseline_markers = self._baseline_action_rows(baseline_executed_orders)
        research_markers = self._research_add_rows(overlay_orders)
        symbols = sorted({str(row["symbol"]) for row in baseline_markers + research_markers})

        fig, axes = plt.subplots(len(symbols), 1, figsize=(14, 4.5 * len(symbols)), sharex=False)
        if len(symbols) == 1:
            axes = [axes]
        legend_handles = [
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#1f77b4", markerfacecolor="#1f77b4", label="O = Open", markersize=6),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#2ca02c", markerfacecolor="#2ca02c", label="A = Add", markersize=6),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#ff7f0e", markerfacecolor="#ff7f0e", label="R = Reduce", markersize=6),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#d62728", markerfacecolor="#d62728", label="C = Close", markersize=6),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#6a3d9a", markerfacecolor="none", label="TA = Test Add", markersize=6),
        ]
        styles = {
            "open": "#1f77b4",
            "add": "#2ca02c",
            "reduce": "#ff7f0e",
            "close": "#d62728",
            "research_add": "#6a3d9a",
        }
        short_label = {
            "open": "O",
            "add": "A",
            "reduce": "R",
            "close": "C",
            "research_add": "TA",
        }
        for ax, symbol in zip(axes, symbols):
            symbol_daily_rows = sorted(
                ((trade_date, payload) for (sym, trade_date), payload in daily_bars.items() if sym == symbol),
                key=lambda item: item[0],
            )
            xs = [row[0] for row in symbol_daily_rows]
            ys = [_to_float(row[1]["close"]) for row in symbol_daily_rows]
            ax.plot(xs, ys, color="#444444", linewidth=1.2)

            rows = [row for row in baseline_markers if row["symbol"] == symbol] + [row for row in research_markers if row["symbol"] == symbol]
            for idx, row in enumerate(sorted(rows, key=lambda item: item["trade_date"])):
                color = styles[row["label"]]
                face = color if row["label"] != "research_add" else "none"
                ax.scatter(
                    row["trade_date"],
                    row["price"],
                    s=30,
                    edgecolors=color,
                    facecolors=face,
                    linewidths=1.0,
                    zorder=5,
                )
                ax.annotate(
                    f"{short_label[row['label']]}\n{row['trade_date'].strftime('%m-%d')}",
                    xy=(row["trade_date"], row["price"]),
                    xytext=(4, -16 if idx % 2 == 0 else 8),
                    textcoords="offset points",
                    fontsize=6,
                    color=color,
                    bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.8},
                )
            ax.set_title(f"{symbol} Daily Close with Baseline/Test Actions")
            ax.grid(alpha=0.2)
            ax.legend(handles=legend_handles, loc="upper left", fontsize=8, framealpha=0.9)
        axes[-1].set_xlabel("Trade Date")
        plt.tight_layout()
        plt.savefig(marker_png, dpi=160)
        plt.close(fig)

        summary = {
            "acceptance_posture": "freeze_v120f_cpo_research_test_baseline_explainer_plots_v1",
            "explainer_csv": str(explainer_csv.relative_to(self.repo_root)),
            "equity_curve_png": str(equity_png.relative_to(self.repo_root)),
            "daily_marker_png": str(marker_png.relative_to(self.repo_root)),
            "baseline_final_equity": round(baseline_equity_curve[-1], 4),
            "research_test_final_equity": round(research_equity_curve[-1], 4),
            "research_test_max_drawdown": round(_max_drawdown(research_equity_curve), 6),
            "explainer_row_count": len(explainer_rows),
        }
        interpretation = [
            "This bundle is the readable explanation layer for the research test baseline replay.",
            "The explainer table keeps baseline actions and research-test adds together so the user can inspect what actually happened by date, symbol, reason, and weight.",
            "The plots are deliberately separate from the broader candidate-comparison plot so they match the single test-baseline question rather than the earlier surviving-candidate comparison.",
        ]
        return CpoResearchTestBaselineExplainerPlotsReport(summary=summary, interpretation=interpretation)


def write_cpo_research_test_baseline_explainer_plots_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CpoResearchTestBaselineExplainerPlotsReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
