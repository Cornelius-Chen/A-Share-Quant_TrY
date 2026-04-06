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
from a_share_quant.strategy.v128s_commercial_aerospace_failure_library_bootstrap_v1 import (
    V128SCommercialAerospaceFailureLibraryBootstrapAnalyzer,
)


@dataclass(slots=True)
class V128UCommercialAerospaceIntradayCollapseOverrideProxyAuditReport:
    summary: dict[str, Any]
    proxy_hit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "proxy_hit_rows": self.proxy_hit_rows,
            "interpretation": self.interpretation,
        }


class V128UCommercialAerospaceIntradayCollapseOverrideProxyAuditAnalyzer:
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

    def analyze(self) -> V128UCommercialAerospaceIntradayCollapseOverrideProxyAuditReport:
        dashboard = V128RCommercialAerospacePrimaryTimechainDashboardAnalyzer(self.repo_root).analyze()
        timechain = V128OCommercialAerospaceTimeChainPreopenEventAuditAnalyzer(self.repo_root).analyze()
        failure_bootstrap = V128SCommercialAerospaceFailureLibraryBootstrapAnalyzer(self.repo_root).analyze()

        order_rows = self._load_csv(self.repo_root / dashboard.summary["orders_csv"])
        daily_rows = self._load_csv(self.daily_path)
        label_rows = self._load_csv(self.label_path)

        timechain_map = {row["execution_trade_date"]: row for row in timechain.execution_day_rows}
        failure_map = {(row["execution_trade_date"], row["symbol"]): row for row in failure_bootstrap.failure_rows}
        daily_map = {(row["trade_date"], row["symbol"]): row for row in daily_rows}
        label_map = {(row["trade_date"], row["symbol"]): row for row in label_rows}

        proxy_hit_rows: list[dict[str, Any]] = []
        total_buy_order_count = 0
        total_buy_notional = 0.0
        total_proxy_notional = 0.0
        total_execution_day_harm = 0.0

        for order in order_rows:
            if order["action"] not in {"open", "add"}:
                continue
            total_buy_order_count += 1
            notional = self._safe_float(order["notional"])
            total_buy_notional += notional

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
            signal_label = label.get("supervised_action_label_pg", "")
            pre_open_status = timechain_map.get(execution_trade_date, {}).get("pre_open_event_status", "no_decisive_event")

            proxy_hit = (
                pre_open_status == "no_decisive_event"
                and signal_label == "de_risk_target"
                and open_to_close_return <= -0.07
                and close_location <= 0.10
            )
            if not proxy_hit:
                continue

            execution_day_harm = notional * abs(open_to_close_return)
            total_proxy_notional += notional
            total_execution_day_harm += execution_day_harm
            failure_row = failure_map.get((execution_trade_date, symbol))
            proxy_hit_rows.append(
                {
                    "signal_trade_date": signal_trade_date,
                    "execution_trade_date": execution_trade_date,
                    "symbol": symbol,
                    "action": order["action"],
                    "notional": round(notional, 4),
                    "open_to_close_return": round(open_to_close_return, 8),
                    "close_location": round(close_location, 8),
                    "signal_label": signal_label,
                    "pre_open_event_status": pre_open_status,
                    "execution_day_harm_estimate": round(execution_day_harm, 4),
                    "matched_failure_id": failure_row["failure_id"] if failure_row else "",
                    "matched_failure_type": failure_row["failure_type"] if failure_row else "",
                }
            )

        retained_failure_ids = {
            row["failure_id"]
            for row in failure_bootstrap.failure_rows
            if row["failure_type"] == "intraday_collapse_override_required"
        }
        proxy_hit_failure_ids = {row["matched_failure_id"] for row in proxy_hit_rows if row["matched_failure_id"]}
        csv_path = (
            self.repo_root
            / "data"
            / "training"
            / "commercial_aerospace_intraday_collapse_override_proxy_hits_v1.csv"
        )
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        if proxy_hit_rows:
            with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(proxy_hit_rows[0].keys()))
                writer.writeheader()
                for row in proxy_hit_rows:
                    writer.writerow(row)

        summary = {
            "acceptance_posture": "freeze_v128u_commercial_aerospace_intraday_collapse_override_proxy_audit_v1",
            "primary_variant": dashboard.summary["variant"],
            "total_buy_order_count": total_buy_order_count,
            "proxy_hit_order_count": len(proxy_hit_rows),
            "proxy_hit_day_count": len({row["execution_trade_date"] for row in proxy_hit_rows}),
            "retained_failure_case_count": len(retained_failure_ids),
            "retained_failure_coverage_rate": round(
                len(proxy_hit_failure_ids & retained_failure_ids) / len(retained_failure_ids), 8
            )
            if retained_failure_ids
            else 0.0,
            "watch_only_trigger_count": max(0, len(proxy_hit_failure_ids - retained_failure_ids)),
            "proxy_notional_share": round(total_proxy_notional / total_buy_notional, 8) if total_buy_notional > 0 else 0.0,
            "execution_day_harm_estimate_total": round(total_execution_day_harm, 4),
            "proxy_hits_csv": str(csv_path.relative_to(self.repo_root)),
            "authoritative_rule": "intraday collapse override proxy is supervision-only because it uses execution-day path information and must not be promoted into lawful replay before minute-level or intraday point-in-time support exists",
        }
        interpretation = [
            "V1.28U tests whether a very narrow supervision-only proxy can isolate the strongest retained intraday collapse failures.",
            "The proxy is intentionally strict: no pre-open decisive adverse event, de-risk-target signal semantics, and a severe execution-day open-to-close collapse with a bottom-decile close location.",
        ]
        return V128UCommercialAerospaceIntradayCollapseOverrideProxyAuditReport(
            summary=summary,
            proxy_hit_rows=proxy_hit_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128UCommercialAerospaceIntradayCollapseOverrideProxyAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128UCommercialAerospaceIntradayCollapseOverrideProxyAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128u_commercial_aerospace_intraday_collapse_override_proxy_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
