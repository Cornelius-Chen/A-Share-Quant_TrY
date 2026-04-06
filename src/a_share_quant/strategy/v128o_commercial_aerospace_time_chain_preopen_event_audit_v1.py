from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v128l_commercial_aerospace_primary_dashboard_v1 import (
    V128LCommercialAerospacePrimaryDashboardAnalyzer,
)


@dataclass(slots=True)
class V128OCommercialAerospaceTimeChainPreopenEventAuditReport:
    summary: dict[str, Any]
    execution_day_rows: list[dict[str, Any]]
    suspicious_order_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "execution_day_rows": self.execution_day_rows,
            "suspicious_order_rows": self.suspicious_order_rows,
            "interpretation": self.interpretation,
        }


class V128OCommercialAerospaceTimeChainPreopenEventAuditAnalyzer:
    ADVERSE_SEMANTICS = {"turning_point_watch", "termination_or_regulation_risk"}
    SUPPORTIVE_SEMANTICS = {"continuation_enabler"}

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_decisive_event_registry_v1.csv"
        )

    @staticmethod
    def _parse_dt(value: str) -> datetime | None:
        if not value:
            return None
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _signal_close_dt(trade_date: str) -> datetime:
        return datetime.strptime(trade_date + " 15:00:00", "%Y%m%d %H:%M:%S")

    @staticmethod
    def _execution_open_dt(trade_date: str) -> datetime:
        return datetime.strptime(trade_date + " 09:30:00", "%Y%m%d %H:%M:%S")

    def _load_registry_rows(self) -> list[dict[str, Any]]:
        with self.registry_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        retained = [row for row in rows if str(row.get("decisive_retained", "")).lower() == "true"]
        for row in retained:
            row["_visible_dt"] = self._parse_dt(row.get("public_release_time", "") or row.get("system_visible_time", ""))
        return retained

    def analyze(self) -> V128OCommercialAerospaceTimeChainPreopenEventAuditReport:
        dashboard = V128LCommercialAerospacePrimaryDashboardAnalyzer(self.repo_root).analyze()
        orders_csv = self.repo_root / dashboard.summary["orders_csv"]
        with orders_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            orders = list(csv.DictReader(handle))
        registry_rows = self._load_registry_rows()

        execution_day_map: dict[str, dict[str, Any]] = {}
        suspicious_order_rows: list[dict[str, Any]] = []

        for order in orders:
            signal_trade_date = order["signal_trade_date"]
            execution_trade_date = order["execution_trade_date"]
            window_start = self._signal_close_dt(signal_trade_date)
            window_end = self._execution_open_dt(execution_trade_date)
            window_events = [
                row for row in registry_rows
                if row["_visible_dt"] is not None and window_start < row["_visible_dt"] <= window_end
            ]
            adverse_events = [row for row in window_events if row["decisive_semantic"] in self.ADVERSE_SEMANTICS]
            supportive_events = [row for row in window_events if row["decisive_semantic"] in self.SUPPORTIVE_SEMANTICS]

            bucket = execution_day_map.setdefault(
                execution_trade_date,
                {
                    "execution_trade_date": execution_trade_date,
                    "signal_trade_dates": set(),
                    "order_count": 0,
                    "buy_count": 0,
                    "sell_count": 0,
                    "overnight_supportive_event_count": 0,
                    "overnight_adverse_event_count": 0,
                    "overnight_supportive_sources": set(),
                    "overnight_adverse_sources": set(),
                },
            )
            bucket["signal_trade_dates"].add(signal_trade_date)
            bucket["order_count"] += 1
            if order["action"] in {"open", "add"}:
                bucket["buy_count"] += 1
            else:
                bucket["sell_count"] += 1
            bucket["overnight_supportive_event_count"] = max(bucket["overnight_supportive_event_count"], len(supportive_events))
            bucket["overnight_adverse_event_count"] = max(bucket["overnight_adverse_event_count"], len(adverse_events))
            for row in supportive_events:
                bucket["overnight_supportive_sources"].add(row["source_name"])
            for row in adverse_events:
                bucket["overnight_adverse_sources"].add(row["source_name"])

            if order["action"] in {"open", "add"} and adverse_events:
                suspicious_order_rows.append(
                    {
                        "signal_trade_date": signal_trade_date,
                        "execution_trade_date": execution_trade_date,
                        "symbol": order["symbol"],
                        "action": order["action"],
                        "reason": order["reason"],
                        "overnight_adverse_event_count": len(adverse_events),
                        "overnight_adverse_sources": " | ".join(sorted({row["source_name"] for row in adverse_events})),
                    }
                )

        execution_day_rows = []
        for trade_date, row in sorted(execution_day_map.items()):
            if row["overnight_adverse_event_count"] > 0:
                status = "adverse_present"
            elif row["overnight_supportive_event_count"] > 0:
                status = "supportive_present"
            else:
                status = "no_decisive_event"
            execution_day_rows.append(
                {
                    "execution_trade_date": trade_date,
                    "signal_trade_dates": "|".join(sorted(row["signal_trade_dates"])),
                    "order_count": row["order_count"],
                    "buy_count": row["buy_count"],
                    "sell_count": row["sell_count"],
                    "overnight_supportive_event_count": row["overnight_supportive_event_count"],
                    "overnight_adverse_event_count": row["overnight_adverse_event_count"],
                    "overnight_supportive_sources": " | ".join(sorted(row["overnight_supportive_sources"])),
                    "overnight_adverse_sources": " | ".join(sorted(row["overnight_adverse_sources"])),
                    "pre_open_event_status": status,
                }
            )

        supportive_days = sum(1 for row in execution_day_rows if row["overnight_supportive_event_count"] > 0)
        adverse_days = sum(1 for row in execution_day_rows if row["overnight_adverse_event_count"] > 0)
        summary = {
            "acceptance_posture": "freeze_v128o_commercial_aerospace_time_chain_preopen_event_audit_v1",
            "primary_variant": dashboard.summary["variant"],
            "execution_day_count": len(execution_day_rows),
            "supportive_execution_day_count": supportive_days,
            "adverse_execution_day_count": adverse_days,
            "suspicious_buy_order_count": len(suspicious_order_rows),
            "authoritative_rule": "overnight_pre_open_event_window_is_signal_close_exclusive_to_execution_open_inclusive",
        }
        interpretation = [
            "V1.28O audits the current commercial-aerospace primary against a strict overnight event window: after the signal-day close and before the next execution-day open.",
            "This does not add a new replay rule yet; it only determines whether any executed buy was exposed to a pre-open decisive adverse event that should have been eligible for veto review.",
        ]
        return V128OCommercialAerospaceTimeChainPreopenEventAuditReport(
            summary=summary,
            execution_day_rows=execution_day_rows,
            suspicious_order_rows=suspicious_order_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128OCommercialAerospaceTimeChainPreopenEventAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128OCommercialAerospaceTimeChainPreopenEventAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128o_commercial_aerospace_time_chain_preopen_event_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
