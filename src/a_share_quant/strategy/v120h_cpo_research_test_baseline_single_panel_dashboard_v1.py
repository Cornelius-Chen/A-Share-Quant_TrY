from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from a_share_quant.strategy.v120g_cpo_research_test_baseline_dashboard_v1 import (
    CpoResearchTestBaselineDashboardAnalyzer,
    CpoResearchTestBaselineDashboardReport,
)
from a_share_quant.strategy.v120f_cpo_research_test_baseline_explainer_plots_v1 import (
    load_json_report,
)


class CpoResearchTestBaselineSinglePanelDashboardAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> CpoResearchTestBaselineDashboardReport:
        base = CpoResearchTestBaselineDashboardAnalyzer(repo_root=self.repo_root).analyze()

        daily_state_path = self.repo_root / base.summary["daily_state_csv"]
        action_strip_path = self.repo_root / base.summary["action_strip_csv"]

        import csv
        from datetime import datetime

        def parse_trade_date(value: str):
            return datetime.strptime(value, "%Y-%m-%d").date()

        with daily_state_path.open("r", encoding="utf-8-sig", newline="") as handle:
            daily_rows = list(csv.DictReader(handle))
        with action_strip_path.open("r", encoding="utf-8-sig", newline="") as handle:
            action_rows = list(csv.DictReader(handle))

        trade_dates = [parse_trade_date(row["trade_date"]) for row in daily_rows]
        equity_curve = [float(row["equity"]) for row in daily_rows]
        cash_curve = [float(row["cash"]) for row in daily_rows]

        held_segments: list[dict[str, object]] = []
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

        png_path = self.repo_root / "reports" / "analysis" / "v120h_cpo_research_test_baseline_single_panel_dashboard_v1.png"
        png_path.parent.mkdir(parents=True, exist_ok=True)

        symbol_order = ["300308", "300502", "300757", "688498"]
        symbol_y = {symbol: idx for idx, symbol in enumerate(symbol_order)}
        colors = {
            "OPEN": "#1f77b4",
            "ADD": "#2ca02c",
            "REDUCE": "#ff7f0e",
            "CLOSE": "#d62728",
            "SADD": "#6a3d9a",
        }

        fig, ax = plt.subplots(figsize=(18, 9))
        ax.plot(trade_dates, equity_curve, color="#111111", linewidth=2.3, label="Equity")
        ax.plot(trade_dates, cash_curve, color="#1f77b4", linewidth=1.6, linestyle="--", label="Cash")
        ax.set_title("CPO Research Test Baseline Single-Panel Dashboard")
        ax.set_ylabel("CNY")
        ax.grid(alpha=0.18)

        y_min = min(min(equity_curve), min(cash_curve))
        y_max = max(max(equity_curve), max(cash_curve))
        y_span = max(y_max - y_min, 1.0)
        for idx, segment in enumerate(held_segments):
            start = segment["start"]
            end = segment["end"]
            x_mid = start + (end - start) / 2
            y_text = y_max - y_span * (0.06 + 0.045 * (idx % 2))
            ax.text(
                x_mid,
                y_text,
                str(segment["label"]),
                ha="center",
                va="center",
                fontsize=8,
                bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "#bbbbbb", "alpha": 0.85},
            )

        ax2 = ax.twinx()
        ax2.set_ylim(-0.7, len(symbol_order) - 0.3)
        ax2.set_yticks(list(symbol_y.values()))
        ax2.set_yticklabels(symbol_order)
        ax2.set_ylabel("Action Track")

        for row in action_rows:
            symbol = row["symbol"]
            if symbol not in symbol_y:
                continue
            dt = parse_trade_date(row["trade_date"])
            label = row["label"]
            weight = float(row["weight"])
            y = symbol_y[symbol]
            color = colors[label]
            facecolor = "white" if label == "SADD" else color
            ax2.scatter(
                dt,
                y,
                s=56,
                edgecolors=color,
                facecolors=facecolor,
                linewidths=1.2,
                zorder=6,
            )
            ax2.annotate(
                f"{symbol} {label} {weight:.1%}\n{dt.strftime('%m-%d')}",
                xy=(dt, y),
                xytext=(4, 11 if label in {"OPEN", "SADD"} else -18),
                textcoords="offset points",
                fontsize=7,
                color=color,
                bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.92},
            )

        legend_handles = [
            Line2D([0], [0], color="#111111", linewidth=2.3, label="Equity"),
            Line2D([0], [0], color="#1f77b4", linewidth=1.6, linestyle="--", label="Cash"),
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

        summary = dict(base.summary)
        summary["acceptance_posture"] = "freeze_v120h_cpo_research_test_baseline_single_panel_dashboard_v1"
        summary["single_panel_dashboard_png"] = str(png_path.relative_to(self.repo_root))
        interpretation = [
            "Single-panel replacement for the earlier split dashboard.",
            "Equity, cash, held-symbol segments, and dated action markers are all plotted in one figure.",
        ]
        return CpoResearchTestBaselineDashboardReport(summary=summary, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: CpoResearchTestBaselineDashboardReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path

