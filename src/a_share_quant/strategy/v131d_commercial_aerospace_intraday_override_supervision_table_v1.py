from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131DCommercialAerospaceIntradayOverrideSupervisionTableReport:
    summary: dict[str, Any]
    supervision_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "supervision_rows": self.supervision_rows,
            "interpretation": self.interpretation,
        }


class V131DCommercialAerospaceIntradayOverrideSupervisionTableAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.dashboard_report_path = (
            repo_root / "reports" / "analysis" / "v128r_commercial_aerospace_primary_timechain_dashboard_v1.json"
        )
        self.timechain_report_path = (
            repo_root / "reports" / "analysis" / "v128o_commercial_aerospace_time_chain_preopen_event_audit_v1.json"
        )
        self.failure_report_path = (
            repo_root / "reports" / "analysis" / "v128s_commercial_aerospace_failure_library_bootstrap_v1.json"
        )
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.label_path = repo_root / "data" / "training" / "commercial_aerospace_phase_geometry_label_table_v1.csv"
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_intraday_override_supervision_rows_v1.csv"
        )

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def _safe_float(value: str | float | int | None) -> float:
        if value in (None, ""):
            return 0.0
        return float(value)

    def analyze(self) -> V131DCommercialAerospaceIntradayOverrideSupervisionTableReport:
        dashboard = json.loads(self.dashboard_report_path.read_text(encoding="utf-8"))
        timechain = json.loads(self.timechain_report_path.read_text(encoding="utf-8"))
        failure_bootstrap = json.loads(self.failure_report_path.read_text(encoding="utf-8"))

        order_rows = self._load_csv(self.repo_root / dashboard["summary"]["orders_csv"])
        daily_rows = self._load_csv(self.daily_path)
        label_rows = self._load_csv(self.label_path)

        daily_map = {(row["trade_date"], row["symbol"]): row for row in daily_rows}
        label_map = {(row["trade_date"], row["symbol"]): row for row in label_rows}
        timechain_map = {row["execution_trade_date"]: row for row in timechain["execution_day_rows"]}
        failure_map = {(row["execution_trade_date"], row["symbol"]): row for row in failure_bootstrap["failure_rows"]}

        supervision_rows: list[dict[str, Any]] = []
        for order in order_rows:
            if order["action"] not in {"open", "add"}:
                continue

            execution_trade_date = order["execution_trade_date"]
            signal_trade_date = order["signal_trade_date"]
            symbol = order["symbol"]
            daily = daily_map.get((execution_trade_date, symbol))
            label = label_map.get((signal_trade_date, symbol))
            if daily is None or label is None:
                continue

            day_open = self._safe_float(daily["open"])
            day_high = self._safe_float(daily["high"])
            day_low = self._safe_float(daily["low"])
            day_close = self._safe_float(daily["close"])
            if day_open <= 0 or day_high <= day_low:
                continue

            open_to_close_return = (day_close / day_open) - 1.0
            close_location = (day_close - day_low) / (day_high - day_low)
            intraday_range_return = (day_high / day_low) - 1.0 if day_low > 0 else 0.0
            close_from_high = (day_close / day_high) - 1.0 if day_high > 0 else 0.0
            gap_from_signal_close = (
                (day_open / self._safe_float(label.get("close"))) - 1.0
                if self._safe_float(label.get("close")) > 0
                else 0.0
            )

            failure_row = failure_map.get((execution_trade_date, symbol))
            if failure_row is not None:
                failure_type = failure_row["failure_type"]
                if failure_type == "intraday_collapse_override_required":
                    supervision_label = "override_positive"
                elif failure_type == "intraday_reversal_watch":
                    supervision_label = "reversal_watch"
                else:
                    supervision_label = "mismatch_watch"
            elif open_to_close_return > -0.02 and close_location > 0.35:
                supervision_label = "clean_control"
                failure_type = ""
            else:
                supervision_label = "ambiguous_non_override"
                failure_type = ""

            timechain_row = timechain_map.get(execution_trade_date, {})
            supervision_rows.append(
                {
                    "signal_trade_date": signal_trade_date,
                    "execution_trade_date": execution_trade_date,
                    "symbol": symbol,
                    "action": order["action"],
                    "reason": order["reason"],
                    "signal_label_pg": label.get("supervised_action_label_pg", ""),
                    "phase_window_semantic": label.get("phase_window_semantic", ""),
                    "regime_proxy_semantic": label.get("regime_proxy_semantic", ""),
                    "event_state": label.get("event_state", ""),
                    "pre_open_event_status": timechain_row.get("pre_open_event_status", "no_decisive_event"),
                    "overnight_adverse_event_count": int(timechain_row.get("overnight_adverse_event_count", 0) or 0),
                    "overnight_supportive_event_count": int(timechain_row.get("overnight_supportive_event_count", 0) or 0),
                    "order_notional": round(self._safe_float(order["notional"]), 4),
                    "weight_vs_initial_capital": round(self._safe_float(order["weight_vs_initial_capital"]), 8),
                    "open_to_close_return": round(open_to_close_return, 8),
                    "close_location": round(close_location, 8),
                    "intraday_range_return": round(intraday_range_return, 8),
                    "close_from_high": round(close_from_high, 8),
                    "gap_from_signal_close_to_open": round(gap_from_signal_close, 8),
                    "forward_return_10": round(self._safe_float(label.get("forward_return_10")), 8),
                    "max_favorable_return_10": round(self._safe_float(label.get("max_favorable_return_10")), 8),
                    "max_adverse_return_10": round(self._safe_float(label.get("max_adverse_return_10")), 8),
                    "failure_type": failure_type,
                    "supervision_label": supervision_label,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(supervision_rows[0].keys()))
            writer.writeheader()
            for row in supervision_rows:
                writer.writerow(row)

        label_counts: dict[str, int] = {}
        for row in supervision_rows:
            label_counts[row["supervision_label"]] = label_counts.get(row["supervision_label"], 0) + 1

        summary = {
            "acceptance_posture": "freeze_v131d_commercial_aerospace_intraday_override_supervision_table_v1",
            "primary_variant": dashboard["summary"]["variant"],
            "buy_execution_row_count": len(supervision_rows),
            "override_positive_count": label_counts.get("override_positive", 0),
            "reversal_watch_count": label_counts.get("reversal_watch", 0),
            "mismatch_watch_count": label_counts.get("mismatch_watch", 0),
            "clean_control_count": label_counts.get("clean_control", 0),
            "ambiguous_non_override_count": label_counts.get("ambiguous_non_override", 0),
            "supervision_rows_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "this table is supervision-only because it uses execution-day path information and must not be merged into lawful EOD replay or training labels",
        }
        interpretation = [
            "V1.31D converts every commercial-aerospace buy execution in the current primary replay into a supervision row for future intraday collapse-override work.",
            "It explicitly separates retained override positives, reversal watches, mismatch watches, clean controls, and ambiguous non-override buys.",
        ]
        return V131DCommercialAerospaceIntradayOverrideSupervisionTableReport(
            summary=summary,
            supervision_rows=supervision_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131DCommercialAerospaceIntradayOverrideSupervisionTableReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131DCommercialAerospaceIntradayOverrideSupervisionTableAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131d_commercial_aerospace_intraday_override_supervision_table_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
