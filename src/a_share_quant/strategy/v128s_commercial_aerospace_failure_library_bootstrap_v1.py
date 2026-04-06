from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v128o_commercial_aerospace_time_chain_preopen_event_audit_v1 import (
    V128OCommercialAerospaceTimeChainPreopenEventAuditAnalyzer,
)
from a_share_quant.strategy.v128r_commercial_aerospace_primary_timechain_dashboard_v1 import (
    V128RCommercialAerospacePrimaryTimechainDashboardAnalyzer,
)


@dataclass(slots=True)
class V128SCommercialAerospaceFailureLibraryBootstrapReport:
    summary: dict[str, Any]
    failure_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "failure_rows": self.failure_rows,
            "interpretation": self.interpretation,
        }


class V128SCommercialAerospaceFailureLibraryBootstrapAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.label_path = repo_root / "data" / "training" / "commercial_aerospace_phase_geometry_label_table_v1.csv"

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def _safe_float(value: str | float | int | None) -> float:
        if value in (None, ""):
            return 0.0
        return float(value)

    def analyze(self) -> V128SCommercialAerospaceFailureLibraryBootstrapReport:
        dashboard = V128RCommercialAerospacePrimaryTimechainDashboardAnalyzer(self.repo_root).analyze()
        timechain = V128OCommercialAerospaceTimeChainPreopenEventAuditAnalyzer(self.repo_root).analyze()

        order_rows = self._load_csv(self.repo_root / dashboard.summary["orders_csv"])
        daily_rows = self._load_csv(self.daily_path)
        label_rows = self._load_csv(self.label_path)

        timechain_map = {row["execution_trade_date"]: row for row in timechain.execution_day_rows}
        daily_map = {(row["trade_date"], row["symbol"]): row for row in daily_rows}
        label_map = {(row["trade_date"], row["symbol"]): row for row in label_rows}

        buy_orders = [row for row in order_rows if row["action"] in {"open", "add"}]
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in buy_orders:
            grouped.setdefault((row["execution_trade_date"], row["signal_trade_date"]), []).append(row)

        failure_rows: list[dict[str, Any]] = []
        for (execution_trade_date, signal_trade_date), rows in sorted(grouped.items()):
            symbols = sorted({row["symbol"] for row in rows})
            order_notional = sum(self._safe_float(row["notional"]) for row in rows)
            timechain_row = timechain_map.get(execution_trade_date, {})
            for symbol in symbols:
                daily = daily_map.get((execution_trade_date, symbol))
                label = label_map.get((signal_trade_date, symbol))
                if daily is None:
                    continue
                day_open = self._safe_float(daily["open"])
                day_high = self._safe_float(daily["high"])
                day_low = self._safe_float(daily["low"])
                day_close = self._safe_float(daily["close"])
                if day_open <= 0 or day_high <= day_low:
                    continue
                open_to_close_return = (day_close / day_open) - 1.0
                close_location = (day_close - day_low) / (day_high - day_low)
                gap_from_signal_close = 0.0
                signal_label = None
                forward_return_10 = 0.0
                max_adverse_return_10 = 0.0
                if label:
                    gap_from_signal_close = (day_open / self._safe_float(label.get("close", day_open))) - 1.0 if self._safe_float(label.get("close", 0.0)) > 0 else 0.0
                    signal_label = label.get("supervised_action_label_pg", "")
                    forward_return_10 = self._safe_float(label.get("forward_return_10"))
                    max_adverse_return_10 = self._safe_float(label.get("max_adverse_return_10"))

                severe_reversal = open_to_close_return <= -0.07 and close_location <= 0.15
                mismatch = signal_label == "de_risk_target"
                if not (severe_reversal or mismatch):
                    continue

                if severe_reversal and mismatch:
                    failure_type = "intraday_collapse_override_required"
                elif severe_reversal:
                    failure_type = "intraday_reversal_watch"
                else:
                    failure_type = "label_execution_mismatch_watch"

                failure_rows.append(
                    {
                        "failure_id": f"{execution_trade_date}_{symbol}",
                        "signal_trade_date": signal_trade_date,
                        "execution_trade_date": execution_trade_date,
                        "symbol": symbol,
                        "failure_type": failure_type,
                        "signal_label": signal_label or "",
                        "pre_open_event_status": timechain_row.get("pre_open_event_status", "no_decisive_event"),
                        "overnight_adverse_event_count": int(timechain_row.get("overnight_adverse_event_count", 0) or 0),
                        "open_to_close_return": round(open_to_close_return, 8),
                        "close_location": round(close_location, 8),
                        "gap_from_signal_close_to_open": round(gap_from_signal_close, 8),
                        "forward_return_10": round(forward_return_10, 8),
                        "max_adverse_return_10": round(max_adverse_return_10, 8),
                        "group_order_notional": round(order_notional, 4),
                        "execution_day_symbols": "/".join(symbols),
                        "suggested_governance_target": (
                            "intraday_collapse_override"
                            if failure_type == "intraday_collapse_override_required"
                            else "failure_watchlist_only"
                        ),
                    }
                )

        failure_rows = sorted(
            failure_rows,
            key=lambda row: (
                0 if row["failure_type"] == "intraday_collapse_override_required" else 1,
                row["execution_trade_date"],
                row["symbol"],
            ),
        )

        csv_path = (
            self.repo_root
            / "data"
            / "training"
            / "commercial_aerospace_failure_library_v1.csv"
        )
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        if failure_rows:
            with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(failure_rows[0].keys()))
                writer.writeheader()
                for row in failure_rows:
                    writer.writerow(row)

        summary = {
            "acceptance_posture": "freeze_v128s_commercial_aerospace_failure_library_bootstrap_v1",
            "primary_variant": dashboard.summary["variant"],
            "buy_order_count": len(buy_orders),
            "failure_case_count": len(failure_rows),
            "intraday_collapse_override_required_count": sum(
                1 for row in failure_rows if row["failure_type"] == "intraday_collapse_override_required"
            ),
            "failure_library_csv": str(csv_path.relative_to(self.repo_root)),
            "authoritative_rule": "failure library captures lawful-but-suspicious execution cases without feeding them back into training labels until separate legality review",
        }
        interpretation = [
            "V1.28S bootstraps a macro-supervision failure library for the current commercial-aerospace primary replay.",
            "Its first target class is the lawful EOD buy that turns into a severe execution-day collapse without any pre-open decisive adverse event, which points to future intraday emergency-exit work rather than time-leakage.",
        ]
        return V128SCommercialAerospaceFailureLibraryBootstrapReport(
            summary=summary,
            failure_rows=failure_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128SCommercialAerospaceFailureLibraryBootstrapReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128SCommercialAerospaceFailureLibraryBootstrapAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128s_commercial_aerospace_failure_library_bootstrap_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
