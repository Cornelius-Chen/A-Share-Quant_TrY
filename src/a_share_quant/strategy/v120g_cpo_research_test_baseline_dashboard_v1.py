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
    _load_daily_bars,
    _max_drawdown,
)
from a_share_quant.strategy.v120f_cpo_research_test_baseline_explainer_plots_v1 import (
    load_json_report,
)


def parse_trade_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class CpoResearchTestBaselineDashboardReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "interpretation": self.interpretation,
        }


class CpoResearchTestBaselineDashboardAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> CpoResearchTestBaselineDashboardReport:
        v113t_payload = load_json_report(self.repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json")
        v114t_payload = load_json_report(self.repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json")
        v120e_payload = load_json_report(self.repo_root / "reports" / "analysis" / "v120e_cpo_research_test_baseline_overlay_replay_v1.json")
        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)

        baseline_day_rows = list(v114t_payload.get("replay_day_rows", []))
        baseline_orders = list(v114t_payload.get("executed_order_rows", []))
        overlay_orders = list(v120e_payload.get("executed_overlay_rows", []))

        baseline_by_exec: dict[str, list[dict[str, Any]]] = {}
        overlay_by_exec: dict[str, list[dict[str, Any]]] = {}
        for row in baseline_orders:
            baseline_by_exec.setdefault(str(row["execution_trade_date"]), []).append(row)
        for row in overlay_orders:
            overlay_by_exec.setdefault(str(row["execution_trade_date"]), []).append(row)

        cash = 1_000_000.0
        positions: dict[str, int] = {}

        trade_dates = []
        equity_curve = []
        cash_curve = []
        held_label_segments: list[dict[str, Any]] = []
        daily_rows: list[dict[str, Any]] = []
        action_rows: list[dict[str, Any]] = []

        current_segment_start = None
        current_segment_label = None

        for day_row in baseline_day_rows:
            trade_date = str(day_row["trade_date"])
            trade_dt = parse_trade_date(trade_date)

            for row in baseline_by_exec.get(trade_date, []):
                symbol = str(row["symbol"])
                side = str(row["action"])
                quantity = int(row["quantity"])
                execution_price = _to_float(row["execution_price"])
                notional = _to_float(row["notional"])
                total_cost = _to_float(row["total_cost"])
                rationale = str(row.get("rationale", ""))
                prev_qty = positions.get(symbol, 0)

                if side == "buy":
                    cash -= notional + total_cost
                    positions[symbol] = prev_qty + quantity
                    label = "OPEN" if prev_qty <= 0 else "ADD"
                else:
                    sell_qty = min(quantity, prev_qty)
                    cash += sell_qty * execution_price - total_cost
                    positions[symbol] = max(0, prev_qty - sell_qty)
                    label = "CLOSE" if rationale == "close_from_holding_veto" or sell_qty >= prev_qty else "REDUCE"

                action_rows.append(
                    {
                        "trade_date": trade_dt,
                        "symbol": symbol,
                        "lane": "baseline",
                        "label": label,
                        "weight": round(notional / 1_000_000.0, 4),
                        "execution_price": execution_price,
                        "detail": rationale,
                    }
                )

            for row in overlay_by_exec.get(trade_date, []):
                symbol = str(row["symbol"])
                quantity = int(row["quantity"])
                execution_price = _to_float(row["execution_price"])
                notional = _to_float(row["notional"])
                total_cost = _to_float(row["total_cost"])
                cash -= notional + total_cost
                positions[symbol] = positions.get(symbol, 0) + quantity
                action_rows.append(
                    {
                        "trade_date": trade_dt,
                        "symbol": symbol,
                        "lane": "research_test_baseline",
                        "label": "SADD",
                        "weight": round(notional / 1_000_000.0, 4),
                        "execution_price": execution_price,
                        "detail": str(row.get("component_names", "")),
                    }
                )

            equity = cash
            held_symbols = []
            for symbol, qty in sorted(positions.items()):
                if qty <= 0:
                    continue
                bar = daily_bars.get((symbol, trade_dt))
                if bar is None:
                    continue
                equity += qty * _to_float(bar["close"])
                held_symbols.append(symbol)

            held_label = ",".join(held_symbols) if held_symbols else "CASH"
            if current_segment_label != held_label:
                if current_segment_start is not None:
                    held_label_segments.append(
                        {
                            "start": current_segment_start,
                            "end": trade_dates[-1],
                            "label": current_segment_label,
                        }
                    )
                current_segment_start = trade_dt
                current_segment_label = held_label

            trade_dates.append(trade_dt)
            equity_curve.append(equity)
            cash_curve.append(cash)
            daily_rows.append(
                {
                    "trade_date": trade_date,
                    "equity": round(equity, 4),
                    "cash": round(cash, 4),
                    "held_symbols": held_label,
                    "position_count": len(held_symbols),
                    "300308_qty": positions.get("300308", 0),
                    "300502_qty": positions.get("300502", 0),
                    "300757_qty": positions.get("300757", 0),
                    "688498_qty": positions.get("688498", 0),
                }
            )

        if current_segment_start is not None and trade_dates:
            held_label_segments.append(
                {
                    "start": current_segment_start,
                    "end": trade_dates[-1],
                    "label": current_segment_label,
                }
            )

        daily_csv = self.repo_root / "data" / "training" / "cpo_research_test_baseline_daily_state_v1.csv"
        daily_csv.parent.mkdir(parents=True, exist_ok=True)
        with daily_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(daily_rows[0].keys()))
            writer.writeheader()
            writer.writerows(daily_rows)

        action_csv = self.repo_root / "data" / "training" / "cpo_research_test_baseline_action_strip_v1.csv"
        with action_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(action_rows[0].keys()))
            writer.writeheader()
            writer.writerows(
                {
                    **row,
                    "trade_date": row["trade_date"].strftime("%Y-%m-%d"),
                }
                for row in action_rows
            )

        png_path = self.repo_root / "reports" / "analysis" / "v120g_cpo_research_test_baseline_dashboard_v1.png"
        png_path.parent.mkdir(parents=True, exist_ok=True)

        symbols = ["300308", "300502", "300757", "688498"]
        y_map = {symbol: idx for idx, symbol in enumerate(symbols)}
        fig, (ax_top, ax_bottom) = plt.subplots(
            2,
            1,
            figsize=(18, 10),
            sharex=True,
            gridspec_kw={"height_ratios": [3.0, 2.2]},
        )

        ax_top.plot(trade_dates, equity_curve, color="#111111", linewidth=2.2, label="Equity")
        ax_top.plot(trade_dates, cash_curve, color="#1f77b4", linewidth=1.6, linestyle="--", label="Cash")
        ax_top.set_title("CPO Research Test Baseline Dashboard")
        ax_top.set_ylabel("CNY")
        ax_top.grid(alpha=0.2)
        ax_top.legend(loc="upper left", fontsize=9)

        y_min, y_max = min(equity_curve + cash_curve), max(equity_curve + cash_curve)
        y_span = max(y_max - y_min, 1.0)
        for idx, segment in enumerate(held_label_segments):
            x_mid = segment["start"] + (segment["end"] - segment["start"]) / 2
            y_text = y_max - y_span * (0.06 + 0.04 * (idx % 2))
            ax_top.text(
                x_mid,
                y_text,
                segment["label"],
                ha="center",
                va="center",
                fontsize=8,
                bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "#bbbbbb", "alpha": 0.8},
            )

        styles = {
            "OPEN": ("#1f77b4", "o"),
            "ADD": ("#2ca02c", "o"),
            "REDUCE": ("#ff7f0e", "o"),
            "CLOSE": ("#d62728", "o"),
            "SADD": ("#6a3d9a", "o"),
        }
        for action in action_rows:
            symbol = action["symbol"]
            if symbol not in y_map:
                continue
            color, marker = styles[action["label"]]
            y = y_map[symbol]
            facecolor = "white" if action["label"] == "SADD" else color
            ax_bottom.scatter(
                action["trade_date"],
                y,
                s=52,
                edgecolors=color,
                facecolors=facecolor,
                linewidths=1.2,
                marker=marker,
                zorder=5,
            )
            ax_bottom.annotate(
                f"{action['label']} {action['weight']:.1%}\n{action['trade_date'].strftime('%m-%d')}",
                xy=(action["trade_date"], y),
                xytext=(4, 10 if action["label"] in {"OPEN", "SADD"} else -18),
                textcoords="offset points",
                fontsize=7,
                color=color,
                bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.9},
            )

        ax_bottom.set_yticks(list(y_map.values()))
        ax_bottom.set_yticklabels(symbols)
        ax_bottom.set_ylabel("Symbol")
        ax_bottom.set_xlabel("Trade Date")
        ax_bottom.grid(alpha=0.2, axis="x")

        legend_handles = [
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#1f77b4", markerfacecolor="#1f77b4", label="OPEN", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#2ca02c", markerfacecolor="#2ca02c", label="ADD", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#ff7f0e", markerfacecolor="#ff7f0e", label="REDUCE", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#d62728", markerfacecolor="#d62728", label="CLOSE", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#6a3d9a", markerfacecolor="white", label="SADD", markersize=7),
        ]
        ax_bottom.legend(handles=legend_handles, loc="upper left", ncol=5, fontsize=8, framealpha=0.9)

        plt.tight_layout()
        plt.savefig(png_path, dpi=180)
        plt.close(fig)

        summary = {
            "acceptance_posture": "freeze_v120g_cpo_research_test_baseline_dashboard_v1",
            "dashboard_png": str(png_path.relative_to(self.repo_root)),
            "daily_state_csv": str(daily_csv.relative_to(self.repo_root)),
            "action_strip_csv": str(action_csv.relative_to(self.repo_root)),
            "research_test_final_equity": round(equity_curve[-1], 4),
            "research_test_max_drawdown": round(_max_drawdown(equity_curve), 6),
            "final_cash": round(cash_curve[-1], 4),
            "action_row_count": len(action_rows),
            "held_segment_count": len(held_label_segments),
        }
        interpretation = [
            "This dashboard is the single-figure explanation layer the user asked for: equity, cash, held-symbol segments, and dated action markers in one place.",
            "Action labels show the stock row, action type, and notional weight versus the initial 1m capital.",
            "The dashboard is still tied to the research test baseline replay grammar and must not be read as an authoritative production strategy chart.",
        ]
        return CpoResearchTestBaselineDashboardReport(summary=summary, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: CpoResearchTestBaselineDashboardReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path

