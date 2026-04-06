from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from a_share_quant.strategy.v115p_cpo_intraday_timing_aware_overlay_replay_v1 import (
    _costs,
    _load_daily_bars,
    _max_drawdown,
    parse_trade_date,
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V120BCpoSurvivingCandidateShadowReplayPlotsReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "interpretation": self.interpretation,
        }


class V120BCpoSurvivingCandidateShadowReplayPlotsAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _baseline_sell_fraction(executed_orders: list[dict[str, Any]]) -> dict[tuple[Any, str], float]:
        positions: dict[str, int] = {}
        fractions: dict[tuple[Any, str], float] = {}
        ordered = sorted(
            executed_orders,
            key=lambda row: (parse_trade_date(str(row["execution_trade_date"])), str(row["symbol"]), str(row["action"])),
        )
        for row in ordered:
            exec_date = parse_trade_date(str(row["execution_trade_date"]))
            symbol = str(row["symbol"])
            action = str(row["action"])
            quantity = int(row["quantity"])
            if action == "buy":
                positions[symbol] = positions.get(symbol, 0) + quantity
                continue
            before_qty = positions.get(symbol, 0)
            fraction = 0.0 if before_qty <= 0 else min(quantity / before_qty, 1.0)
            fractions[(exec_date, symbol)] = fraction
            positions[symbol] = max(0, before_qty - quantity)
        return fractions

    def _simulate_equity_curve(
        self,
        *,
        baseline_executed_orders: list[dict[str, Any]],
        overlay_orders: list[dict[str, Any]],
        baseline_day_rows: list[dict[str, Any]],
        daily_bars: dict[tuple[str, Any], dict[str, Any]],
    ) -> list[float]:
        baseline_sell_fraction = self._baseline_sell_fraction(baseline_executed_orders)
        trade_dates = [parse_trade_date(str(row["trade_date"])) for row in baseline_day_rows]
        baseline_orders_by_exec: dict[Any, list[dict[str, Any]]] = {}
        overlay_orders_by_exec: dict[Any, list[dict[str, Any]]] = {}
        for row in baseline_executed_orders:
            baseline_orders_by_exec.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)
        for row in overlay_orders:
            overlay_orders_by_exec.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)

        cash = 1_000_000.0
        positions: dict[str, int] = {}
        equity_curve: list[float] = []
        for trade_date in trade_dates:
            for row in baseline_orders_by_exec.get(trade_date, []):
                symbol = str(row["symbol"])
                quantity = int(row["quantity"])
                action = str(row["action"])
                execution_price = _to_float(row["execution_price"])
                rationale = str(row.get("rationale", ""))
                if action == "buy":
                    notional = quantity * execution_price
                    cash -= notional + _costs(action="buy", notional=notional)["total_cost"]
                    positions[symbol] = positions.get(symbol, 0) + quantity
                else:
                    current_qty = positions.get(symbol, 0)
                    if current_qty <= 0:
                        continue
                    if rationale == "close_from_holding_veto":
                        sell_qty = current_qty
                    elif rationale == "reduce_from_board_state_episode":
                        fraction = baseline_sell_fraction.get((trade_date, symbol), 0.0)
                        sell_qty = int((current_qty * fraction) // 100) * 100
                        if sell_qty <= 0:
                            sell_qty = min(current_qty, 100 if current_qty >= 100 else current_qty)
                    else:
                        sell_qty = min(current_qty, quantity)
                    sell_qty = min(current_qty, sell_qty)
                    if sell_qty <= 0:
                        continue
                    notional = sell_qty * execution_price
                    cash += notional - _costs(action="sell", notional=notional)["total_cost"]
                    positions[symbol] = max(0, current_qty - sell_qty)

            for row in overlay_orders_by_exec.get(trade_date, []):
                symbol = str(row["symbol"])
                quantity = int(row["quantity"])
                execution_price = _to_float(row["execution_price"])
                notional = quantity * execution_price
                cash -= notional + _costs(action="buy", notional=notional)["total_cost"]
                positions[symbol] = positions.get(symbol, 0) + quantity

            market_value = 0.0
            for symbol, quantity in positions.items():
                bar = daily_bars.get((symbol, trade_date))
                if bar is None:
                    continue
                market_value += quantity * _to_float(bar["close"])
            equity_curve.append(cash + market_value)
        return equity_curve

    @staticmethod
    def _baseline_action_marker_rows(executed_orders: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
                    "execution_trade_date": exec_date,
                    "execution_price": execution_price,
                    "action_label": label,
                }
            )
        return rows

    @staticmethod
    def _shadow_marker_rows(overlay_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, Any, float], list[str]] = {}
        for row in overlay_rows:
            key = (
                str(row["symbol"]),
                parse_trade_date(str(row["execution_trade_date"])),
                round(_to_float(row["execution_price"]), 4),
            )
            grouped.setdefault(key, []).append(str(row["candidate_name"]))
        marker_rows: list[dict[str, Any]] = []
        for (symbol, exec_date, exec_price), candidates in sorted(grouped.items()):
            short_count = len(candidates)
            marker_rows.append(
                {
                    "symbol": symbol,
                    "execution_trade_date": exec_date,
                    "execution_price": exec_price,
                    "action_label": f"SAx{short_count}",
                }
            )
        return marker_rows

    def analyze(
        self,
        *,
        v113t_payload: dict[str, Any],
        v114t_payload: dict[str, Any],
        v120a_payload: dict[str, Any],
    ) -> V120BCpoSurvivingCandidateShadowReplayPlotsReport:
        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)
        baseline_day_rows = list(v114t_payload.get("replay_day_rows", []))
        baseline_executed_orders = list(v114t_payload.get("executed_order_rows", []))
        baseline_equity_curve = [_to_float(row["equity_after_close"]) for row in baseline_day_rows]
        trade_dates = [parse_trade_date(str(row["trade_date"])) for row in baseline_day_rows]
        overlay_rows = list(v120a_payload.get("overlay_order_rows", []))
        candidate_names = sorted({str(row["candidate_name"]) for row in overlay_rows})

        equity_png = self.repo_root / "reports" / "analysis" / "v120b_cpo_surviving_candidate_shadow_equity_curve_v1.png"
        daily_png = self.repo_root / "reports" / "analysis" / "v120b_cpo_surviving_candidate_daily_close_markers_v1.png"

        plt.figure(figsize=(12, 6))
        plt.plot(trade_dates, baseline_equity_curve, label="baseline_v114t", linewidth=2.2, color="#111111")
        summary_rows = {str(row["candidate_name"]): row for row in list(v120a_payload.get("candidate_summary_rows", []))}
        for candidate_name in candidate_names:
            candidate_orders = [row for row in overlay_rows if str(row["candidate_name"]) == candidate_name]
            candidate_curve = self._simulate_equity_curve(
                baseline_executed_orders=baseline_executed_orders,
                overlay_orders=candidate_orders,
                baseline_day_rows=baseline_day_rows,
                daily_bars=daily_bars,
            )
            label = f"{candidate_name} ({summary_rows[candidate_name]['final_equity']:.0f})"
            plt.plot(trade_dates, candidate_curve, label=label, linewidth=1.7)
        plt.title("CPO Surviving Candidate Shadow Replay Comparison")
        plt.xlabel("Trade Date")
        plt.ylabel("Equity")
        plt.legend(fontsize=8)
        plt.tight_layout()
        equity_png.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(equity_png, dpi=160)
        plt.close()

        symbols = sorted({str(row["symbol"]) for row in overlay_rows})
        baseline_marker_rows = self._baseline_action_marker_rows(baseline_executed_orders)
        shadow_marker_rows = self._shadow_marker_rows(overlay_rows)
        marker_style = {
            "open": {"color": "#1f77b4", "facecolors": "#1f77b4"},
            "add": {"color": "#2ca02c", "facecolors": "#2ca02c"},
            "reduce": {"color": "#ff7f0e", "facecolors": "#ff7f0e"},
            "close": {"color": "#d62728", "facecolors": "#d62728"},
            "shadow": {"color": "#6a3d9a", "facecolors": "none"},
        }
        subplot_count = max(1, len(symbols))
        fig, axes = plt.subplots(subplot_count, 1, figsize=(14, 5 * subplot_count), sharex=False)
        if subplot_count == 1:
            axes = [axes]
        legend_handles = [
            Line2D([0], [0], marker="o", color="none", markeredgecolor=marker_style["open"]["color"], markerfacecolor=marker_style["open"]["facecolors"], label="O = Open", markersize=6),
            Line2D([0], [0], marker="o", color="none", markeredgecolor=marker_style["add"]["color"], markerfacecolor=marker_style["add"]["facecolors"], label="A = Add", markersize=6),
            Line2D([0], [0], marker="o", color="none", markeredgecolor=marker_style["reduce"]["color"], markerfacecolor=marker_style["reduce"]["facecolors"], label="R = Reduce", markersize=6),
            Line2D([0], [0], marker="o", color="none", markeredgecolor=marker_style["close"]["color"], markerfacecolor=marker_style["close"]["facecolors"], label="C = Close", markersize=6),
            Line2D([0], [0], marker="o", color="none", markeredgecolor=marker_style["shadow"]["color"], markerfacecolor="none", label="SA = Shadow Add", markersize=6),
        ]
        for ax, symbol in zip(axes, symbols):
            symbol_rows = sorted(
                [(trade_date, payload) for (sym, trade_date), payload in daily_bars.items() if sym == symbol],
                key=lambda item: item[0],
            )
            xs = [trade_date for trade_date, _ in symbol_rows]
            ys = [_to_float(payload["close"]) for _, payload in symbol_rows]
            ax.plot(xs, ys, color="#444444", linewidth=1.2, label=f"{symbol} close")
            symbol_baseline = [row for row in baseline_marker_rows if str(row["symbol"]) == symbol]
            for row in symbol_baseline:
                action_label = str(row["action_label"])
                style = marker_style[action_label]
                exec_date = row["execution_trade_date"]
                exec_price = _to_float(row["execution_price"])
                ax.scatter(
                    exec_date,
                    exec_price,
                    s=28,
                    marker="o",
                    edgecolors=style["color"],
                    facecolors=style["facecolors"],
                    linewidths=0.9,
                    zorder=4,
                )
                ax.annotate(
                    f"{action_label[0].upper()}\n{exec_date.strftime('%m-%d')}",
                    xy=(exec_date, exec_price),
                    xytext=(4, 8),
                    textcoords="offset points",
                    fontsize=6,
                    color=style["color"],
                    bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.75},
                )
            symbol_shadow = [row for row in shadow_marker_rows if str(row["symbol"]) == symbol]
            for idx, row in enumerate(symbol_shadow):
                style = marker_style["shadow"]
                exec_date = row["execution_trade_date"]
                exec_price = _to_float(row["execution_price"])
                ax.scatter(
                    exec_date,
                    exec_price,
                    s=34,
                    marker="o",
                    edgecolors=style["color"],
                    facecolors=style["facecolors"],
                    linewidths=1.1,
                    zorder=5,
                )
                ax.annotate(
                    f"SA\n{exec_date.strftime('%m-%d')}",
                    xy=(exec_date, exec_price),
                    xytext=(4, -16 if idx % 2 == 0 else -24),
                    textcoords="offset points",
                    fontsize=6,
                    color=style["color"],
                    bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.75},
                )
            ax.set_title(f"{symbol} Daily Close with Action Markers")
            ax.set_ylabel("Close")
            ax.legend(handles=legend_handles, loc="upper left", fontsize=8, framealpha=0.9)
            ax.grid(alpha=0.2)
        axes[-1].set_xlabel("Trade Date")
        plt.tight_layout()
        plt.savefig(daily_png, dpi=160)
        plt.close(fig)

        summary = {
            "acceptance_posture": "freeze_v120b_cpo_surviving_candidate_shadow_replay_plots_v1",
            "equity_curve_png": str(equity_png.relative_to(self.repo_root)),
            "daily_close_marker_png": str(daily_png.relative_to(self.repo_root)),
            "candidate_count_plotted": len(candidate_names),
            "symbol_count_plotted": len(symbols),
            "baseline_max_drawdown": _max_drawdown(baseline_equity_curve),
        }
        interpretation = [
            "V1.20B turns the unified shadow replay comparison into two visual surfaces: total equity curves and symbol-level daily-close marker charts.",
            "Markers are execution-date markers, not same-day intraday fills. This plot is intentionally aligned with the conservative T+1 comparison grammar used in V120A.",
            "The user can now inspect both payoff dispersion and whether each candidate tends to add at obviously bad or obviously useful daily locations.",
        ]
        return V120BCpoSurvivingCandidateShadowReplayPlotsReport(summary=summary, interpretation=interpretation)


def write_report(*, reports_dir: Path, result: V120BCpoSurvivingCandidateShadowReplayPlotsReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / "v120b_cpo_surviving_candidate_shadow_replay_plots_v1.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V120BCpoSurvivingCandidateShadowReplayPlotsAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v120a_payload=json.loads((repo_root / "reports" / "analysis" / "v120a_cpo_surviving_candidate_shadow_replay_comparison_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(reports_dir=repo_root / "reports" / "analysis", result=result)
    print(output_path)


if __name__ == "__main__":
    main()
