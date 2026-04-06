from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def parse_trade_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


class CpoResearchTestBaselineCompactDashboardAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> dict:
        daily_csv = self.repo_root / "data" / "training" / "cpo_research_test_baseline_daily_state_v1.csv"
        action_csv = self.repo_root / "data" / "training" / "cpo_research_test_baseline_action_strip_v1.csv"

        with daily_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            daily_rows = list(csv.DictReader(handle))
        with action_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            action_rows = list(csv.DictReader(handle))

        trade_dates = [parse_trade_date(row["trade_date"]) for row in daily_rows]
        equity_curve = [float(row["equity"]) for row in daily_rows]
        cash_curve = [float(row["cash"]) for row in daily_rows]

        held_segments = []
        current_label = None
        current_start = None
        for row in daily_rows:
            label = row["held_symbols"]
            dt = parse_trade_date(row["trade_date"])
            if label != current_label:
                if current_start is not None:
                    held_segments.append({"start": current_start, "end": prev_dt, "label": current_label})
                current_start = dt
                current_label = label
            prev_dt = dt
        if current_start is not None:
            held_segments.append({"start": current_start, "end": prev_dt, "label": current_label})

        png_path = self.repo_root / "reports" / "analysis" / "v120i_cpo_research_test_baseline_compact_dashboard_v1.png"
        json_path = self.repo_root / "reports" / "analysis" / "v120i_cpo_research_test_baseline_compact_dashboard_v1.json"
        png_path.parent.mkdir(parents=True, exist_ok=True)

        symbol_order = ["300308", "300502", "300757", "688498"]
        symbol_y = {symbol: idx for idx, symbol in enumerate(symbol_order)}
        color_map = {
            "OPEN": "#1f77b4",
            "ADD": "#2ca02c",
            "REDUCE": "#ff7f0e",
            "CLOSE": "#d62728",
            "SADD": "#6a3d9a",
        }

        fig = plt.figure(figsize=(20, 9))
        ax = fig.add_axes([0.06, 0.10, 0.64, 0.82])
        ax.plot(trade_dates, equity_curve, color="#111111", linewidth=2.2, label="Equity")
        ax.plot(trade_dates, cash_curve, color="#1f77b4", linewidth=1.5, linestyle="--", label="Cash")
        ax.set_title("CPO Research Test Baseline Compact Dashboard")
        ax.set_ylabel("CNY")
        ax.grid(alpha=0.18)

        y_min = min(min(equity_curve), min(cash_curve))
        y_max = max(max(equity_curve), max(cash_curve))
        y_span = max(y_max - y_min, 1.0)
        for idx, segment in enumerate(held_segments):
            x_mid = segment["start"] + (segment["end"] - segment["start"]) / 2
            y_text = y_max - y_span * (0.05 + 0.04 * (idx % 2))
            ax.text(
                x_mid,
                y_text,
                str(segment["label"]),
                ha="center",
                va="center",
                fontsize=8,
                bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "#bbbbbb", "alpha": 0.8},
            )

        ax2 = ax.twinx()
        ax2.set_ylim(-0.7, len(symbol_order) - 0.3)
        ax2.set_yticks(list(symbol_y.values()))
        ax2.set_yticklabels(symbol_order)
        ax2.set_ylabel("Action Track")

        compact_rows = []
        for idx, row in enumerate(action_rows, start=1):
            symbol = row["symbol"]
            if symbol not in symbol_y:
                continue
            dt = parse_trade_date(row["trade_date"])
            label = row["label"]
            weight = float(row["weight"])
            y = symbol_y[symbol]
            color = color_map[label]
            facecolor = "white" if label == "SADD" else color
            ax2.scatter(
                dt,
                y,
                s=48,
                edgecolors=color,
                facecolors=facecolor,
                linewidths=1.2,
                zorder=6,
            )
            ax2.annotate(
                f"{idx}",
                xy=(dt, y),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=7,
                color=color,
                bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "none", "alpha": 0.9},
            )
            compact_rows.append(
                {
                    "id": idx,
                    "trade_date": row["trade_date"],
                    "symbol": symbol,
                    "label": label,
                    "weight": weight,
                }
            )

        legend_handles = [
            Line2D([0], [0], color="#111111", linewidth=2.2, label="Equity"),
            Line2D([0], [0], color="#1f77b4", linewidth=1.5, linestyle="--", label="Cash"),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#1f77b4", markerfacecolor="#1f77b4", label="OPEN", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#2ca02c", markerfacecolor="#2ca02c", label="ADD", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#ff7f0e", markerfacecolor="#ff7f0e", label="REDUCE", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#d62728", markerfacecolor="#d62728", label="CLOSE", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#6a3d9a", markerfacecolor="white", label="SADD", markersize=7),
        ]
        ax.legend(handles=legend_handles, loc="upper left", ncol=7, fontsize=8, framealpha=0.9)

        text_lines = ["ID  DATE   TICKER  ACT   WGT"]
        for row in compact_rows:
            text_lines.append(
                f"{row['id']:>2}  {row['trade_date'][5:]}  {row['symbol']}  {row['label']:<6} {row['weight']:>5.1%}"
            )
        fig.text(
            0.73,
            0.90,
            "\n".join(text_lines),
            va="top",
            ha="left",
            fontsize=8,
            family="monospace",
            bbox={"boxstyle": "round,pad=0.4", "fc": "white", "ec": "#cccccc", "alpha": 0.95},
        )

        plt.savefig(png_path, dpi=180)
        plt.close(fig)

        payload = {
            "summary": {
                "acceptance_posture": "freeze_v120i_cpo_research_test_baseline_compact_dashboard_v1",
                "compact_dashboard_png": str(png_path.relative_to(self.repo_root)),
                "action_count": len(compact_rows),
            },
            "compact_rows": compact_rows,
        }
        with json_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
        return payload

