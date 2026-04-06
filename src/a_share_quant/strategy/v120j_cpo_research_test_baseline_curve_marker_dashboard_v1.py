from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def parse_trade_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


class CpoResearchTestBaselineCurveMarkerDashboardAnalyzer:
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
        equity_by_date = {parse_trade_date(row["trade_date"]): float(row["equity"]) for row in daily_rows}
        held_by_date = {parse_trade_date(row["trade_date"]): row["held_symbols"] for row in daily_rows}

        colors = {
            "OPEN": "#1f77b4",
            "ADD": "#2ca02c",
            "REDUCE": "#ff7f0e",
            "CLOSE": "#d62728",
            "SADD": "#6a3d9a",
        }
        short = {
            "OPEN": "O",
            "ADD": "A",
            "REDUCE": "R",
            "CLOSE": "C",
            "SADD": "SA",
        }

        png_path = self.repo_root / "reports" / "analysis" / "v120j_cpo_research_test_baseline_curve_marker_dashboard_v1.png"
        json_path = self.repo_root / "reports" / "analysis" / "v120j_cpo_research_test_baseline_curve_marker_dashboard_v1.json"
        png_path.parent.mkdir(parents=True, exist_ok=True)

        fig, ax = plt.subplots(figsize=(18, 8))
        ax.plot(trade_dates, equity_curve, color="#111111", linewidth=2.3, label="Equity")
        ax.plot(trade_dates, cash_curve, color="#1f77b4", linewidth=1.5, linestyle="--", label="Cash")
        ax.set_title("CPO Research Test Baseline Curve-Marker Dashboard")
        ax.set_ylabel("CNY")
        ax.grid(alpha=0.18)

        y_min = min(min(equity_curve), min(cash_curve))
        y_max = max(max(equity_curve), max(cash_curve))
        y_span = max(y_max - y_min, 1.0)

        segments = []
        current_label = None
        current_start = None
        for row in daily_rows:
            dt = parse_trade_date(row["trade_date"])
            label = row["held_symbols"]
            if label != current_label:
                if current_start is not None:
                    segments.append({"start": current_start, "end": prev_dt, "label": current_label})
                current_start = dt
                current_label = label
            prev_dt = dt
        if current_start is not None:
            segments.append({"start": current_start, "end": prev_dt, "label": current_label})

        for idx, segment in enumerate(segments):
            x_mid = segment["start"] + (segment["end"] - segment["start"]) / 2
            y_text = y_max - y_span * (0.05 + 0.04 * (idx % 2))
            ax.text(
                x_mid,
                y_text,
                str(segment["label"]),
                ha="center",
                va="center",
                fontsize=8,
                bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "#bbbbbb", "alpha": 0.85},
            )

        actions_by_date = {}
        for row in action_rows:
            dt = parse_trade_date(row["trade_date"])
            actions_by_date.setdefault(dt, []).append(row)

        marker_rows = []
        for dt, rows in sorted(actions_by_date.items(), key=lambda item: item[0]):
            equity = equity_by_date.get(dt)
            if equity is None:
                continue
            ordered = sorted(rows, key=lambda r: (r["symbol"], r["label"]))
            for idx, row in enumerate(ordered):
                label = row["label"]
                color = colors[label]
                facecolor = "white" if label == "SADD" else color
                ax.scatter(
                    dt,
                    equity,
                    s=58,
                    edgecolors=color,
                    facecolors=facecolor,
                    linewidths=1.2,
                    zorder=6,
                )
                y_offset = 10 + (idx % 4) * 12 if idx % 2 == 0 else -(12 + (idx % 4) * 12)
                text = f"{row['symbol']} {short[label]} {float(row['weight']):.1%}\n{dt.strftime('%m-%d')}"
                ax.annotate(
                    text,
                    xy=(dt, equity),
                    xytext=(4, y_offset),
                    textcoords="offset points",
                    fontsize=7,
                    color=color,
                    bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.92},
                )
                marker_rows.append(
                    {
                        "trade_date": dt.strftime("%Y-%m-%d"),
                        "symbol": row["symbol"],
                        "label": label,
                        "weight": float(row["weight"]),
                        "equity": equity,
                        "held_symbols_after_close": held_by_date.get(dt, ""),
                    }
                )

        legend_handles = [
            Line2D([0], [0], color="#111111", linewidth=2.3, label="Equity"),
            Line2D([0], [0], color="#1f77b4", linewidth=1.5, linestyle="--", label="Cash"),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#1f77b4", markerfacecolor="#1f77b4", label="OPEN", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#2ca02c", markerfacecolor="#2ca02c", label="ADD", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#ff7f0e", markerfacecolor="#ff7f0e", label="REDUCE", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#d62728", markerfacecolor="#d62728", label="CLOSE", markersize=7),
            Line2D([0], [0], marker="o", color="none", markeredgecolor="#6a3d9a", markerfacecolor="white", label="SADD", markersize=7),
        ]
        ax.legend(handles=legend_handles, loc="upper left", ncol=7, fontsize=8, framealpha=0.9)

        plt.tight_layout()
        plt.savefig(png_path, dpi=180)
        plt.close(fig)

        payload = {
            "summary": {
                "acceptance_posture": "freeze_v120j_cpo_research_test_baseline_curve_marker_dashboard_v1",
                "curve_marker_dashboard_png": str(png_path.relative_to(self.repo_root)),
                "marker_count": len(marker_rows),
                "final_equity": round(equity_curve[-1], 4),
                "final_cash": round(cash_curve[-1], 4),
            },
            "marker_rows": marker_rows,
        }
        with json_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
        return payload

