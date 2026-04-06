from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from a_share_quant.strategy.v132u_commercial_aerospace_local_1min_state_transition_audit_v1 import (
    _running_state,
    _symbol_to_archive_member,
)


STATE_STYLE = {
    "mild_override_watch": {"color": "#7b61ff", "label": "Mild", "marker": "o"},
    "reversal_watch": {"color": "#ff8c42", "label": "Reversal", "marker": "^"},
    "severe_override_positive": {"color": "#111111", "label": "Severe", "marker": "X"},
}


@dataclass(slots=True)
class V132YCommercialAerospaceIntradaySeedCasePanelReport:
    summary: dict[str, Any]
    case_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "case_rows": self.case_rows,
            "interpretation": self.interpretation,
        }


class V132YCommercialAerospaceIntradaySeedCasePanelAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_supervision_registry_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.case_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_seed_case_panel_rows_v1.csv"
        )

    def _load_registry_rows(self) -> list[dict[str, str]]:
        with self.registry_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def _load_session(self, trade_date: str, symbol: str) -> list[dict[str, Any]]:
        zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
        member_name = _symbol_to_archive_member(symbol)
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open(member_name, "r") as member:
                rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]

        base_open = float(rows[0][3])
        highs: list[float] = []
        lows: list[float] = []
        session_rows: list[dict[str, Any]] = []
        for idx, row in enumerate(rows, start=1):
            current_open = float(row[3])
            current_close = float(row[4])
            current_high = float(row[5])
            current_low = float(row[6])
            highs.append(current_high)
            lows.append(current_low)
            high_so_far = max(highs)
            low_so_far = min(lows)
            current_return = current_close / base_open - 1.0
            drawdown = low_so_far / base_open - 1.0
            close_location = 0.5 if high_so_far == low_so_far else (current_close - low_so_far) / (high_so_far - low_so_far)
            state = _running_state(
                current_return=current_return,
                drawdown=drawdown,
                close_location=close_location,
            )
            session_rows.append(
                {
                    "minute_index": idx,
                    "clock_time": row[0].split(" ")[1] if " " in row[0] else row[0],
                    "open_to_now_return": current_return,
                    "drawdown_so_far": drawdown,
                    "close_location_so_far": close_location,
                    "state": state,
                    "open_price": current_open,
                    "close_price": current_close,
                }
            )
        return session_rows

    def analyze(self) -> V132YCommercialAerospaceIntradaySeedCasePanelReport:
        registry_rows = self._load_registry_rows()
        case_rows: list[dict[str, Any]] = []

        fig, axes = plt.subplots(3, 2, figsize=(16, 12), sharex=False, sharey=False)
        axes_flat = axes.flatten()

        for ax, registry_row in zip(axes_flat, registry_rows):
            execution_trade_date = registry_row["execution_trade_date"]
            symbol = registry_row["symbol"]
            session_rows = self._load_session(execution_trade_date, symbol)
            minute_idx = [row["minute_index"] for row in session_rows]
            returns = [row["open_to_now_return"] * 100.0 for row in session_rows]

            ax.plot(minute_idx, returns, color="#1f77b4", linewidth=1.8)
            ax.axhline(0.0, color="#9aa0a6", linewidth=0.8, linestyle="--")

            first_state_minute: dict[str, int] = {}
            for row in session_rows:
                state = row["state"]
                if state in STATE_STYLE and state not in first_state_minute:
                    first_state_minute[state] = row["minute_index"]

            for state, first_minute in first_state_minute.items():
                style = STATE_STYLE[state]
                y_value = returns[first_minute - 1]
                ax.scatter(
                    [first_minute],
                    [y_value],
                    color=style["color"],
                    marker=style["marker"],
                    s=52,
                    zorder=3,
                )
                ax.axvline(first_minute, color=style["color"], linewidth=0.9, linestyle=":")

            title = (
                f"{execution_trade_date} {symbol} {registry_row['action']} | "
                f"{registry_row['severity_tier']}"
            )
            subtitle = f"{registry_row['phase_window_semantic']} | {registry_row['event_state']}"
            ax.set_title(f"{title}\n{subtitle}", fontsize=9)
            ax.set_xlabel("Minute")
            ax.set_ylabel("Return %")
            ax.grid(alpha=0.18)

            case_row = {
                "signal_trade_date": registry_row["signal_trade_date"],
                "execution_trade_date": execution_trade_date,
                "symbol": symbol,
                "action": registry_row["action"],
                "severity_tier": registry_row["severity_tier"],
                "phase_window_semantic": registry_row["phase_window_semantic"],
                "event_state": registry_row["event_state"],
                "first_mild_minute": first_state_minute.get("mild_override_watch", ""),
                "first_reversal_minute": first_state_minute.get("reversal_watch", ""),
                "first_severe_minute": first_state_minute.get("severe_override_positive", ""),
                "session_close_return_pct": round(returns[-1], 4),
                "session_low_drawdown_pct": round(min(row["drawdown_so_far"] for row in session_rows) * 100.0, 4),
            }
            case_rows.append(case_row)

        legend_handles = []
        legend_labels = []
        for state, style in STATE_STYLE.items():
            handle = plt.Line2D(
                [0],
                [0],
                color=style["color"],
                marker=style["marker"],
                linestyle=":",
                linewidth=1.0,
                markersize=7,
            )
            legend_handles.append(handle)
            legend_labels.append(style["label"])
        fig.legend(legend_handles, legend_labels, loc="upper center", ncol=3, frameon=False)
        fig.suptitle("Commercial Aerospace Intraday Seed Cases", fontsize=14, y=0.98)
        fig.tight_layout(rect=(0, 0, 1, 0.96))

        png_path = self.repo_root / "reports" / "analysis" / "v132y_commercial_aerospace_intraday_seed_case_panel_v1.png"
        png_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(png_path, dpi=180, bbox_inches="tight")
        plt.close(fig)

        self.case_csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.case_csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(case_rows[0].keys()))
            writer.writeheader()
            writer.writerows(case_rows)

        summary = {
            "acceptance_posture": "freeze_v132y_commercial_aerospace_intraday_seed_case_panel_v1",
            "seed_case_count": len(case_rows),
            "panel_png": str(png_path.relative_to(self.repo_root)),
            "case_rows_csv": str(self.case_csv_path.relative_to(self.repo_root)),
            "authoritative_rule": "the minute governance branch should remain visually inspectable through canonical seed sessions before any future lawful intraday execution work is attempted",
        }
        interpretation = [
            "V1.32Y packages the six canonical commercial-aerospace minute seed sessions into a single visual case panel.",
            "The panel is a governance aid: it makes the severe / reversal / mild action ladder inspectable without altering the lawful EOD replay.",
        ]
        return V132YCommercialAerospaceIntradaySeedCasePanelReport(
            summary=summary,
            case_rows=case_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132YCommercialAerospaceIntradaySeedCasePanelReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132YCommercialAerospaceIntradaySeedCasePanelAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132y_commercial_aerospace_intraday_seed_case_panel_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
