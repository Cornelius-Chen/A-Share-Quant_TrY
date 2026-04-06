from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def parse_trade_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


class CpoResearchTestBaselineTopDrawdownDashboardAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _top_drawdown_segments(rows: list[dict], top_n: int = 3) -> list[dict]:
        segments = []
        peak_eq = rows[0]["equity"]
        peak_date = rows[0]["trade_date"]
        trough_eq = rows[0]["equity"]
        trough_date = rows[0]["trade_date"]
        in_drawdown = False

        for row in rows[1:]:
            eq = row["equity"]
            if eq >= peak_eq:
                if in_drawdown and trough_eq < peak_eq:
                    segments.append(
                        {
                            "peak_date": peak_date,
                            "peak_equity": peak_eq,
                            "trough_date": trough_date,
                            "trough_equity": trough_eq,
                            "drawdown": (peak_eq - trough_eq) / peak_eq,
                            "drawdown_amount": peak_eq - trough_eq,
                        }
                    )
                peak_eq = eq
                peak_date = row["trade_date"]
                trough_eq = eq
                trough_date = row["trade_date"]
                in_drawdown = False
            else:
                in_drawdown = True
                if eq < trough_eq:
                    trough_eq = eq
                    trough_date = row["trade_date"]

        if in_drawdown and trough_eq < peak_eq:
            segments.append(
                {
                    "peak_date": peak_date,
                    "peak_equity": peak_eq,
                    "trough_date": trough_date,
                    "trough_equity": trough_eq,
                    "drawdown": (peak_eq - trough_eq) / peak_eq,
                    "drawdown_amount": peak_eq - trough_eq,
                }
            )
        segments.sort(key=lambda x: x["drawdown"], reverse=True)
        return segments[:top_n]

    def analyze(self) -> dict:
        daily_csv = self.repo_root / "data" / "training" / "cpo_research_test_baseline_daily_state_v1.csv"
        with daily_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            daily_rows = list(csv.DictReader(handle))

        rows = [
            {
                "trade_date": parse_trade_date(row["trade_date"]),
                "equity": float(row["equity"]),
                "cash": float(row["cash"]),
                "held_symbols": row["held_symbols"],
            }
            for row in daily_rows
        ]

        trade_dates = [row["trade_date"] for row in rows]
        equity_curve = [row["equity"] for row in rows]
        cash_curve = [row["cash"] for row in rows]
        top_dd = self._top_drawdown_segments(rows, top_n=3)

        png_path = self.repo_root / "reports" / "analysis" / "v120k_cpo_research_test_baseline_top_drawdown_dashboard_v1.png"
        json_path = self.repo_root / "reports" / "analysis" / "v120k_cpo_research_test_baseline_top_drawdown_dashboard_v1.json"
        png_path.parent.mkdir(parents=True, exist_ok=True)

        fig, ax = plt.subplots(figsize=(18, 8))
        ax.plot(trade_dates, equity_curve, color="#111111", linewidth=2.3, label="Equity")
        ax.plot(trade_dates, cash_curve, color="#1f77b4", linewidth=1.5, linestyle="--", label="Cash")
        ax.set_title("CPO Research Test Baseline Top Drawdowns")
        ax.set_ylabel("CNY")
        ax.grid(alpha=0.18)

        shade_colors = ["#ffcccc", "#ffe7bf", "#fff4b3"]
        text_y_fracs = [0.15, 0.23, 0.31]
        y_min = min(min(equity_curve), min(cash_curve))
        y_max = max(max(equity_curve), max(cash_curve))
        y_span = max(y_max - y_min, 1.0)

        dd_rows = []
        for idx, segment in enumerate(top_dd, start=1):
            ax.axvspan(segment["peak_date"], segment["trough_date"], color=shade_colors[idx - 1], alpha=0.35)
            mid_x = segment["peak_date"] + (segment["trough_date"] - segment["peak_date"]) / 2
            text_y = y_max - y_span * text_y_fracs[idx - 1]
            text = (
                f"#{idx} {segment['peak_date'].strftime('%Y-%m-%d')} -> {segment['trough_date'].strftime('%Y-%m-%d')}\n"
                f"DD {segment['drawdown']:.2%} | {segment['drawdown_amount'] / 10000:.2f}万"
            )
            ax.text(
                mid_x,
                text_y,
                text,
                ha="center",
                va="center",
                fontsize=9,
                bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#999999", "alpha": 0.92},
            )
            dd_rows.append(
                {
                    "rank": idx,
                    "peak_date": segment["peak_date"].strftime("%Y-%m-%d"),
                    "peak_equity": round(segment["peak_equity"], 4),
                    "trough_date": segment["trough_date"].strftime("%Y-%m-%d"),
                    "trough_equity": round(segment["trough_equity"], 4),
                    "drawdown": round(segment["drawdown"], 6),
                    "drawdown_amount": round(segment["drawdown_amount"], 4),
                }
            )

        legend_handles = [
            Line2D([0], [0], color="#111111", linewidth=2.3, label="Equity"),
            Line2D([0], [0], color="#1f77b4", linewidth=1.5, linestyle="--", label="Cash"),
            Line2D([0], [0], color=shade_colors[0], linewidth=8, alpha=0.5, label="Top DD #1"),
            Line2D([0], [0], color=shade_colors[1], linewidth=8, alpha=0.5, label="Top DD #2"),
            Line2D([0], [0], color=shade_colors[2], linewidth=8, alpha=0.5, label="Top DD #3"),
        ]
        ax.legend(handles=legend_handles, loc="upper left", fontsize=9, framealpha=0.9)

        plt.tight_layout()
        plt.savefig(png_path, dpi=180)
        plt.close(fig)

        payload = {
            "summary": {
                "acceptance_posture": "freeze_v120k_cpo_research_test_baseline_top_drawdown_dashboard_v1",
                "top_drawdown_dashboard_png": str(png_path.relative_to(self.repo_root)),
                "top_drawdown_count": len(dd_rows),
            },
            "top_drawdown_rows": dd_rows,
        }
        with json_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
        return payload

