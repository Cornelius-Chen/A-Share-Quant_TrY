from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from a_share_quant.strategy.v128l_commercial_aerospace_primary_dashboard_v1 import (
    V128LCommercialAerospacePrimaryDashboardAnalyzer,
)
from a_share_quant.strategy.v128o_commercial_aerospace_time_chain_preopen_event_audit_v1 import (
    V128OCommercialAerospaceTimeChainPreopenEventAuditAnalyzer,
)


@dataclass(slots=True)
class V128RCommercialAerospacePrimaryTimechainDashboardReport:
    summary: dict[str, Any]
    grouped_action_rows: list[dict[str, Any]]
    top_drawdown_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "grouped_action_rows": self.grouped_action_rows,
            "top_drawdown_rows": self.top_drawdown_rows,
            "interpretation": self.interpretation,
        }


class V128RCommercialAerospacePrimaryTimechainDashboardAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.base_analyzer = V128LCommercialAerospacePrimaryDashboardAnalyzer(repo_root)
        self.timechain_analyzer = V128OCommercialAerospaceTimeChainPreopenEventAuditAnalyzer(repo_root)

    @staticmethod
    def _parse_trade_date(value: str) -> datetime.date:
        return datetime.strptime(value, "%Y%m%d").date()

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def _write_csv(output_path: Path, rows: list[dict[str, Any]]) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    @staticmethod
    def _marker_size(abs_net_weight: float) -> float:
        if abs_net_weight >= 0.10:
            return 140.0
        if abs_net_weight >= 0.05:
            return 95.0
        return 60.0

    @staticmethod
    def _compact_event_tag(status: str) -> str:
        if status == "supportive_present":
            return "pre:sup"
        if status == "adverse_present":
            return "pre:adv"
        return "pre:none"

    def _build_grouped_rows(
        self,
        *,
        order_rows: list[dict[str, Any]],
        equity_by_date: dict[str, float],
        timechain_rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        grouped: dict[str, dict[str, Any]] = {}
        timechain_map = {row["execution_trade_date"]: row for row in timechain_rows}
        for row in order_rows:
            execution_trade_date = row["execution_trade_date"]
            bucket = grouped.setdefault(
                execution_trade_date,
                {
                    "execution_trade_date": execution_trade_date,
                    "signal_trade_dates": set(),
                    "open_count": 0,
                    "add_count": 0,
                    "reduce_count": 0,
                    "close_count": 0,
                    "buy_weight": 0.0,
                    "sell_weight": 0.0,
                    "symbols": [],
                    "equity": equity_by_date.get(execution_trade_date, 0.0),
                },
            )
            bucket["signal_trade_dates"].add(row["signal_trade_date"])
            action = row["action"]
            bucket[f"{action}_count"] += 1
            weight = float(row["weight_vs_initial_capital"])
            if action in {"open", "add"}:
                bucket["buy_weight"] += weight
            else:
                bucket["sell_weight"] += weight
            bucket["symbols"].append(row["symbol"])

        grouped_rows: list[dict[str, Any]] = []
        for execution_trade_date, bucket in sorted(grouped.items()):
            signal_dates = sorted(bucket["signal_trade_dates"])
            signal_display = signal_dates[0] if len(signal_dates) == 1 else f"{signal_dates[0]}|+{len(signal_dates) - 1}"
            trade_date = execution_trade_date
            symbols = sorted(set(bucket["symbols"]))
            display_symbols = "/".join(symbols[:3]) + (f"/+{len(symbols) - 3}" if len(symbols) > 3 else "")
            net_weight = bucket["buy_weight"] - bucket["sell_weight"]
            timechain = timechain_map.get(execution_trade_date, {})
            pre_open_status = timechain.get("pre_open_event_status", "no_decisive_event")
            grouped_rows.append(
                {
                    "signal_trade_dates": "|".join(signal_dates),
                    "signal_trade_date_display": signal_display,
                    "execution_trade_date": execution_trade_date,
                    "signal_execution_display": f"{signal_dates[0][4:6]}-{signal_dates[0][6:8]}>{trade_date[4:6]}-{trade_date[6:8]}",
                    "pre_open_event_status": pre_open_status,
                    "pre_open_event_tag": self._compact_event_tag(pre_open_status),
                    "overnight_supportive_event_count": timechain.get("overnight_supportive_event_count", 0),
                    "overnight_adverse_event_count": timechain.get("overnight_adverse_event_count", 0),
                    "overnight_supportive_sources": timechain.get("overnight_supportive_sources", ""),
                    "overnight_adverse_sources": timechain.get("overnight_adverse_sources", ""),
                    "open_count": bucket["open_count"],
                    "add_count": bucket["add_count"],
                    "reduce_count": bucket["reduce_count"],
                    "close_count": bucket["close_count"],
                    "buy_weight": round(bucket["buy_weight"], 8),
                    "sell_weight": round(bucket["sell_weight"], 8),
                    "net_weight": round(net_weight, 8),
                    "display_symbols": display_symbols,
                    "equity": round(bucket["equity"], 4),
                }
            )
        return grouped_rows

    def _plot_dashboard(
        self,
        *,
        daily_rows: list[dict[str, Any]],
        grouped_action_rows: list[dict[str, Any]],
        output_path: Path,
    ) -> None:
        trade_dates = [self._parse_trade_date(row["trade_date"]) for row in daily_rows]
        equity_curve = [float(row["equity"]) for row in daily_rows]
        cash_curve = [float(row["cash"]) for row in daily_rows]
        board_curve = [float(row["board_overlay_equity"]) for row in daily_rows]
        equity_by_date = {self._parse_trade_date(row["trade_date"]): float(row["equity"]) for row in daily_rows}

        fig, ax = plt.subplots(figsize=(22, 10))
        ax.plot(trade_dates, equity_curve, color="#111111", linewidth=2.4, label="Equity")
        ax.plot(trade_dates, cash_curve, color="#1f77b4", linewidth=1.6, linestyle="--", label="Cash")
        ax.plot(trade_dates, board_curve, color="#7f8c8d", linewidth=1.8, linestyle="-.", label="Board Overlay")
        ax.set_title("Commercial Aerospace Primary Replay Dashboard: tail_weakdrift_full (Timechain)")
        ax.set_ylabel("CNY")
        ax.grid(alpha=0.18)

        styles = {
            "buy": {"color": "#1f77b4", "marker": "s", "label": "Buy Day"},
            "sell": {"color": "#ff7f0e", "marker": "^", "label": "Sell Day"},
            "mixed": {"color": "#6a3d9a", "marker": "D", "label": "Mixed Day"},
        }
        labeled_rows = sorted(grouped_action_rows, key=lambda row: (-abs(float(row["net_weight"])), row["execution_trade_date"]))[:12]
        labeled_dates = {row["execution_trade_date"] for row in labeled_rows}

        for idx, row in enumerate(grouped_action_rows):
            dt = self._parse_trade_date(row["execution_trade_date"])
            equity = equity_by_date[dt]
            buy_count = int(row["open_count"]) + int(row["add_count"])
            sell_count = int(row["reduce_count"]) + int(row["close_count"])
            if buy_count > 0 and sell_count == 0:
                key = "buy"
            elif sell_count > 0 and buy_count == 0:
                key = "sell"
            else:
                key = "mixed"
            style = styles[key]
            color = style["color"]
            marker_size = self._marker_size(abs(float(row["net_weight"])))
            ax.scatter(
                dt,
                equity,
                s=marker_size,
                marker=style["marker"],
                edgecolors=color,
                facecolors="white",
                linewidths=1.7,
                zorder=7,
            )
            if row["execution_trade_date"] in labeled_dates:
                if buy_count > 0 and sell_count == 0:
                    short_label = "B"
                elif sell_count > 0 and buy_count == 0:
                    short_label = "S"
                else:
                    short_label = "M"
                offset_y = (12 + (idx % 3) * 8) if idx % 2 == 0 else -(14 + (idx % 3) * 8)
                ax.annotate(
                    f"{row['signal_execution_display']} {short_label}\n{row['display_symbols']}\n{row['pre_open_event_tag']}",
                    xy=(dt, equity),
                    xytext=(4, offset_y),
                    textcoords="offset points",
                    fontsize=6.2,
                    color=color,
                    bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.92},
                )

        legend_handles = [
            Line2D([0], [0], color="#111111", linewidth=2.4, label="Equity"),
            Line2D([0], [0], color="#1f77b4", linewidth=1.6, linestyle="--", label="Cash"),
            Line2D([0], [0], color="#7f8c8d", linewidth=1.8, linestyle="-.", label="Board Overlay"),
            Line2D([0], [0], marker="s", color="none", markeredgecolor="#1f77b4", markerfacecolor="white", label="Buy Day", markersize=7),
            Line2D([0], [0], marker="^", color="none", markeredgecolor="#ff7f0e", markerfacecolor="white", label="Sell Day", markersize=7),
            Line2D([0], [0], marker="D", color="none", markeredgecolor="#6a3d9a", markerfacecolor="white", label="Mixed Day", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#555555", markerfacecolor="white", label="Small <5%", markersize=6),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#555555", markerfacecolor="white", label="Medium 5-10%", markersize=8),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#555555", markerfacecolor="white", label="Large >10%", markersize=10),
        ]
        ax.legend(handles=legend_handles, loc="upper left", ncol=5, fontsize=8, framealpha=0.92)

        plt.tight_layout()
        plt.savefig(output_path, dpi=180)
        plt.close(fig)

    def analyze(self) -> V128RCommercialAerospacePrimaryTimechainDashboardReport:
        base_report = self.base_analyzer.analyze()
        timechain_report = self.timechain_analyzer.analyze()

        daily_rows = self._load_csv(self.repo_root / base_report.summary["daily_state_csv"])
        order_rows = self._load_csv(self.repo_root / base_report.summary["orders_csv"])
        equity_by_date = {row["trade_date"]: float(row["equity"]) for row in daily_rows}
        grouped_action_rows = self._build_grouped_rows(
            order_rows=order_rows,
            equity_by_date=equity_by_date,
            timechain_rows=timechain_report.execution_day_rows,
        )

        grouped_csv_path = (
            self.repo_root
            / "data"
            / "training"
            / "commercial_aerospace_tail_weakdrift_full_timechain_grouped_actions_v1.csv"
        )
        png_path = self.repo_root / "reports" / "analysis" / "v128r_commercial_aerospace_primary_timechain_dashboard_v1.png"

        self._write_csv(grouped_csv_path, grouped_action_rows)
        self._plot_dashboard(daily_rows=daily_rows, grouped_action_rows=grouped_action_rows, output_path=png_path)

        summary = {
            "acceptance_posture": "freeze_v128r_commercial_aerospace_primary_timechain_dashboard_v1",
            "variant": base_report.summary["variant"],
            "initial_capital": base_report.summary["initial_capital"],
            "final_equity": base_report.summary["final_equity"],
            "max_drawdown": base_report.summary["max_drawdown"],
            "executed_order_count": base_report.summary["executed_order_count"],
            "daily_state_csv": base_report.summary["daily_state_csv"],
            "orders_csv": base_report.summary["orders_csv"],
            "timechain_grouped_actions_csv": str(grouped_csv_path.relative_to(self.repo_root)),
            "dashboard_png": str(png_path.relative_to(self.repo_root)),
            "supportive_execution_day_count": timechain_report.summary["supportive_execution_day_count"],
            "adverse_execution_day_count": timechain_report.summary["adverse_execution_day_count"],
            "suspicious_buy_order_count": timechain_report.summary["suspicious_buy_order_count"],
            "authoritative_rule": "plot labels must distinguish signal_date from execution_date and expose pre-open decisive-event status",
        }
        interpretation = [
            "V1.28R is a transparency upgrade on top of the frozen commercial-aerospace primary replay; it does not change economics.",
            "Every grouped action label now distinguishes signal_date from execution_date and shows whether a decisive supportive or adverse event was visible before the open.",
        ]
        return V128RCommercialAerospacePrimaryTimechainDashboardReport(
            summary=summary,
            grouped_action_rows=grouped_action_rows,
            top_drawdown_rows=base_report.top_drawdown_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128RCommercialAerospacePrimaryTimechainDashboardReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128RCommercialAerospacePrimaryTimechainDashboardAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128r_commercial_aerospace_primary_timechain_dashboard_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
