from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v132c_commercial_aerospace_local_1min_seed_window_extraction_v1 import (
    _symbol_to_archive_member,
)


def _safe_int(value: Any) -> int | None:
    if value in ("", None):
        return None
    return int(value)


def _calc_costs(notional: float, action: str) -> dict[str, float]:
    commission_rate = 0.0003
    min_commission = 5.0
    stamp_tax_rate = 0.001 if action == "sell" else 0.0
    slippage_bps = 5.0
    commission = max(min_commission, notional * commission_rate) if notional > 0 else 0.0
    stamp_tax = notional * stamp_tax_rate
    slippage = notional * (slippage_bps / 10000.0)
    total_cost = commission + stamp_tax + slippage
    return {
        "commission": round(commission, 4),
        "stamp_tax": round(stamp_tax, 4),
        "slippage": round(slippage, 4),
        "total_cost": round(total_cost, 4),
    }


@dataclass(slots=True)
class V134CCommercialAerospaceIntradaySeedSimulatorReport:
    summary: dict[str, Any]
    session_rows: list[dict[str, Any]]
    order_rows: list[dict[str, Any]]
    acceptance_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "session_rows": self.session_rows,
            "order_rows": self.order_rows,
            "acceptance_rows": self.acceptance_rows,
            "interpretation": self.interpretation,
        }


class V134CCommercialAerospaceIntradaySeedSimulatorAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.case_panel_path = (
            repo_root / "reports" / "analysis" / "v132y_commercial_aerospace_intraday_seed_case_panel_v1.json"
        )
        self.registry_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_supervision_registry_v1.csv"
        )
        self.orders_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_orders_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_seed_simulator_orders_v1.csv"
        )
        self.output_sessions_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_seed_simulator_sessions_v1.csv"
        )

    def _load_case_rows(self) -> list[dict[str, Any]]:
        payload = json.loads(self.case_panel_path.read_text(encoding="utf-8"))
        return payload["case_rows"]

    def _load_registry_by_session(self) -> dict[tuple[str, str], dict[str, str]]:
        with self.registry_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            return {
                (row["execution_trade_date"], row["symbol"]): row
                for row in csv.DictReader(handle)
            }

    def _load_order_by_session(self) -> dict[tuple[str, str], dict[str, str]]:
        with self.orders_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            return {
                (row["execution_trade_date"], row["symbol"]): row
                for row in csv.DictReader(handle)
            }

    def _load_full_session_rows(self, trade_date: str, symbol: str) -> list[dict[str, Any]]:
        zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
        member_name = _symbol_to_archive_member(symbol)
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open(member_name, "r") as member:
                raw_rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]
        session_rows: list[dict[str, Any]] = []
        for idx, row in enumerate(raw_rows, start=1):
            session_rows.append(
                {
                    "minute_index": idx,
                    "timestamp": row[0],
                    "open_px": float(row[3]),
                    "close_px": float(row[4]),
                    "high_px": float(row[5]),
                    "low_px": float(row[6]),
                    "volume": float(row[7]),
                    "amount": float(row[8]),
                }
            )
        return session_rows

    def analyze(self) -> V134CCommercialAerospaceIntradaySeedSimulatorReport:
        case_rows = self._load_case_rows()
        registry_by_session = self._load_registry_by_session()
        order_by_session = self._load_order_by_session()

        session_rows: list[dict[str, Any]] = []
        order_rows: list[dict[str, Any]] = []
        executable_session_count = 0
        pending_out_of_window_count = 0
        severe_execution_count = 0
        reversal_execution_count = 0
        mild_watch_count = 0

        for case_row in case_rows:
            trade_date = case_row["execution_trade_date"]
            symbol = case_row["symbol"]
            session_key = (trade_date, symbol)
            registry_row = registry_by_session[session_key]
            order_row = order_by_session[session_key]
            full_session_rows = self._load_full_session_rows(trade_date, symbol)

            quantity = int(float(order_row["quantity"]))
            entry_price = float(order_row["execution_price"])
            entry_notional = float(order_row["notional"])
            remaining_quantity = quantity
            filled_steps = 0

            first_mild = _safe_int(case_row["first_mild_minute"])
            first_reversal = _safe_int(case_row["first_reversal_minute"])
            first_severe = _safe_int(case_row["first_severe_minute"])

            trigger_specs = [
                ("mild_override_watch", first_mild),
                ("reversal_watch", first_reversal),
                ("severe_override_positive", first_severe),
            ]
            ordered_trigger_specs = sorted(
                [item for item in trigger_specs if item[1] is not None],
                key=lambda item: int(item[1]),
            )

            for trigger_tier, trigger_minute in ordered_trigger_specs:
                if trigger_tier == "mild_override_watch":
                    mild_watch_count += 1
                    continue

                fill_minute = trigger_minute + 1
                if fill_minute > len(full_session_rows):
                    pending_out_of_window_count += 1
                    continue

                if remaining_quantity <= 0:
                    continue

                fill_row = full_session_rows[fill_minute - 1]
                fill_price = float(fill_row["open_px"])
                if trigger_tier == "reversal_watch":
                    sell_quantity = remaining_quantity // 2
                    if sell_quantity <= 0:
                        sell_quantity = remaining_quantity
                else:
                    sell_quantity = remaining_quantity
                sell_notional = sell_quantity * fill_price
                costs = _calc_costs(sell_notional, action="sell")
                pnl_before_cost = sell_quantity * (fill_price - entry_price)
                pnl_after_cost = pnl_before_cost - costs["total_cost"]

                order_rows.append(
                    {
                        "execution_trade_date": trade_date,
                        "symbol": symbol,
                        "trigger_tier": trigger_tier,
                        "trigger_minute": trigger_minute,
                        "trigger_ts": full_session_rows[trigger_minute - 1]["timestamp"],
                        "fill_minute": fill_minute,
                        "fill_ts": fill_row["timestamp"],
                        "fill_price": round(fill_price, 4),
                        "sell_quantity": sell_quantity,
                        "sell_notional": round(sell_notional, 4),
                        "commission": costs["commission"],
                        "stamp_tax": costs["stamp_tax"],
                        "slippage": costs["slippage"],
                        "total_cost": costs["total_cost"],
                        "entry_price": round(entry_price, 4),
                        "pnl_before_cost": round(pnl_before_cost, 4),
                        "pnl_after_cost": round(pnl_after_cost, 4),
                    }
                )

                remaining_quantity -= sell_quantity
                filled_steps += 1
                executable_session_count += 1
                if trigger_tier == "severe_override_positive":
                    severe_execution_count += 1
                elif trigger_tier == "reversal_watch":
                    reversal_execution_count += 1

            severe_pending = first_severe is not None and first_severe + 1 > len(full_session_rows)
            reversal_pending = first_reversal is not None and first_reversal + 1 > len(full_session_rows)
            session_rows.append(
                {
                    "signal_trade_date": registry_row["signal_trade_date"],
                    "execution_trade_date": trade_date,
                    "symbol": symbol,
                    "severity_tier": registry_row["severity_tier"],
                    "phase_window_semantic": registry_row["phase_window_semantic"],
                    "event_state": registry_row["event_state"],
                    "entry_action": registry_row["action"],
                    "entry_quantity": quantity,
                    "entry_price": round(entry_price, 4),
                    "entry_notional": round(entry_notional, 4),
                    "first_mild_minute": first_mild if first_mild is not None else "",
                    "first_reversal_minute": first_reversal if first_reversal is not None else "",
                    "first_severe_minute": first_severe if first_severe is not None else "",
                    "filled_step_count": filled_steps,
                    "remaining_quantity_after_sim": remaining_quantity,
                    "severe_pending_out_of_window": severe_pending,
                    "reversal_pending_out_of_window": reversal_pending,
                }
            )

        self.output_orders_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_orders_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(order_rows[0].keys()))
            writer.writeheader()
            writer.writerows(order_rows)

        with self.output_sessions_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        total_exit_notional = round(sum(float(row["sell_notional"]) for row in order_rows), 4)
        total_cost = round(sum(float(row["total_cost"]) for row in order_rows), 4)
        total_pnl_after_cost = round(sum(float(row["pnl_after_cost"]) for row in order_rows), 4)

        acceptance_rows = [
            {
                "acceptance_item": "canonical_seed_session_count",
                "status": "pass" if len(session_rows) == 6 else "fail",
                "detail": f"seed_session_count = {len(session_rows)}",
            },
            {
                "acceptance_item": "same_bar_execution_forbidden",
                "status": "pass",
                "detail": "all simulated fills occur strictly on trigger_minute + 1",
            },
            {
                "acceptance_item": "deterministic_seed_order_rows",
                "status": "pass" if len(order_rows) > 0 else "fail",
                "detail": f"order_row_count = {len(order_rows)}",
            },
            {
                "acceptance_item": "first_hour_boundary_explicit",
                "status": "pass",
                "detail": f"pending_out_of_window_count = {pending_out_of_window_count}",
            },
        ]

        summary = {
            "acceptance_posture": "build_v134c_commercial_aerospace_intraday_seed_simulator_v1",
            "seed_session_count": len(session_rows),
            "simulated_order_count": len(order_rows),
            "executable_session_count": executable_session_count,
            "pending_out_of_window_count": pending_out_of_window_count,
            "severe_execution_count": severe_execution_count,
            "reversal_execution_count": reversal_execution_count,
            "mild_watch_count": mild_watch_count,
            "total_exit_notional": total_exit_notional,
            "total_cost": total_cost,
            "total_pnl_after_cost": total_pnl_after_cost,
            "session_csv": str(self.output_sessions_csv.relative_to(self.repo_root)),
            "orders_csv": str(self.output_orders_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_seed_simulator_ready_for_deterministic_seed_audit",
        }
        interpretation = [
            "V1.34C instantiates the first canonical-seed intraday shadow simulator under the phase-2 rules.",
            "The simulator remains intentionally narrow: it only processes canonical seed sessions, executes on next-bar open, and makes out-of-window trigger limits explicit instead of hiding them.",
        ]
        return V134CCommercialAerospaceIntradaySeedSimulatorReport(
            summary=summary,
            session_rows=session_rows,
            order_rows=order_rows,
            acceptance_rows=acceptance_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CCommercialAerospaceIntradaySeedSimulatorReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CCommercialAerospaceIntradaySeedSimulatorAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134c_commercial_aerospace_intraday_seed_simulator_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
