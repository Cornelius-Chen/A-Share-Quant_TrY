from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v132u_commercial_aerospace_local_1min_state_transition_audit_v1 import (
    _running_state,
    _symbol_to_archive_member,
)
from a_share_quant.strategy.v134c_commercial_aerospace_intraday_seed_simulator_v1 import _calc_costs


def _round_lot_quantity(open_px: float, reference_notional: float) -> int:
    raw_quantity = int(reference_notional // open_px)
    lot_quantity = (raw_quantity // 100) * 100
    if lot_quantity <= 0:
        return 0
    return lot_quantity


@dataclass(slots=True)
class V134LCommercialAerospaceIntradayBroaderHitSimulatorReport:
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


class V134LCommercialAerospaceIntradayBroaderHitSimulatorAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.hit_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_local_1min_session_expansion_hits_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.reference_notional = 100000.0
        self.output_sessions_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_broader_hit_simulator_sessions_v1.csv"
        )
        self.output_orders_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_broader_hit_simulator_orders_v1.csv"
        )

    def _load_hit_rows(self) -> list[dict[str, Any]]:
        with self.hit_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def _load_full_session_rows(self, trade_date: str, symbol: str) -> list[dict[str, Any]]:
        zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
        member_name = _symbol_to_archive_member(symbol)
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open(member_name, "r") as member:
                raw_rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]
        return [
            {
                "minute_index": idx,
                "timestamp": row[0],
                "open_px": float(row[3]),
                "close_px": float(row[4]),
                "high_px": float(row[5]),
                "low_px": float(row[6]),
            }
            for idx, row in enumerate(raw_rows, start=1)
        ]

    def _detect_state_onsets(self, session_rows: list[dict[str, Any]]) -> dict[str, int | None]:
        base_open = float(session_rows[0]["open_px"])
        highs: list[float] = []
        lows: list[float] = []
        first_onset = {
            "mild_override_watch": None,
            "reversal_watch": None,
            "severe_override_positive": None,
        }
        for row in session_rows:
            highs.append(float(row["high_px"]))
            lows.append(float(row["low_px"]))
            high_so_far = max(highs)
            low_so_far = min(lows)
            current_close = float(row["close_px"])
            current_return = current_close / base_open - 1.0
            drawdown = low_so_far / base_open - 1.0
            close_location = 0.5 if high_so_far == low_so_far else (current_close - low_so_far) / (high_so_far - low_so_far)
            state = _running_state(
                current_return=current_return,
                drawdown=drawdown,
                close_location=close_location,
            )
            if state != "neutral" and first_onset[state] is None:
                first_onset[state] = int(row["minute_index"])
        return first_onset

    def analyze(self) -> V134LCommercialAerospaceIntradayBroaderHitSimulatorReport:
        hit_rows = self._load_hit_rows()
        session_rows: list[dict[str, Any]] = []
        order_rows: list[dict[str, Any]] = []
        executable_session_count = 0
        zero_quantity_session_count = 0
        severe_execution_count = 0
        reversal_execution_count = 0
        total_same_day_loss_avoided = 0.0
        pending_out_of_window_count = 0

        for hit_row in hit_rows:
            trade_date = hit_row["trade_date"]
            symbol = hit_row["symbol"]
            full_session_rows = self._load_full_session_rows(trade_date, symbol)
            if not full_session_rows:
                continue

            entry_price = float(full_session_rows[0]["open_px"])
            quantity = _round_lot_quantity(entry_price, self.reference_notional)
            if quantity <= 0:
                zero_quantity_session_count += 1
                continue

            onsets = self._detect_state_onsets(full_session_rows)
            remaining_quantity = quantity
            filled_steps = 0

            ordered_trigger_specs = sorted(
                [
                    ("reversal_watch", onsets["reversal_watch"]),
                    ("severe_override_positive", onsets["severe_override_positive"]),
                ],
                key=lambda item: (10**9 if item[1] is None else int(item[1])),
            )

            for trigger_tier, trigger_minute in ordered_trigger_specs:
                if trigger_minute is None:
                    continue
                fill_minute = int(trigger_minute) + 1
                if fill_minute > len(full_session_rows):
                    pending_out_of_window_count += 1
                    continue
                if remaining_quantity <= 0:
                    continue
                fill_row = full_session_rows[fill_minute - 1]
                fill_price = float(fill_row["open_px"])
                if trigger_tier == "reversal_watch":
                    sell_quantity = max(100, (remaining_quantity // 2 // 100) * 100)
                    sell_quantity = min(sell_quantity, remaining_quantity)
                else:
                    sell_quantity = remaining_quantity
                sell_notional = sell_quantity * fill_price
                costs = _calc_costs(sell_notional, action="sell")
                pnl_before_cost = sell_quantity * (fill_price - entry_price)
                pnl_after_cost = pnl_before_cost - costs["total_cost"]
                order_rows.append(
                    {
                        "trade_date": trade_date,
                        "symbol": symbol,
                        "predicted_tier": hit_row["predicted_tier"],
                        "trigger_tier": trigger_tier,
                        "trigger_minute": int(trigger_minute),
                        "fill_minute": fill_minute,
                        "trigger_ts": full_session_rows[int(trigger_minute) - 1]["timestamp"],
                        "fill_ts": fill_row["timestamp"],
                        "entry_price": round(entry_price, 4),
                        "fill_price": round(fill_price, 4),
                        "sell_quantity": sell_quantity,
                        "sell_notional": round(sell_notional, 4),
                        "commission": costs["commission"],
                        "stamp_tax": costs["stamp_tax"],
                        "slippage": costs["slippage"],
                        "total_cost": costs["total_cost"],
                        "pnl_after_cost": round(pnl_after_cost, 4),
                    }
                )
                remaining_quantity -= sell_quantity
                filled_steps += 1
                executable_session_count += 1
                if trigger_tier == "reversal_watch":
                    reversal_execution_count += 1
                else:
                    severe_execution_count += 1

            close_price = float(full_session_rows[-1]["close_px"])
            simulated_close_value = remaining_quantity * close_price
            baseline_hold_pnl = quantity * (close_price - entry_price)
            simulated_pnl = (
                sum(
                    row["sell_quantity"] * (float(row["fill_price"]) - entry_price) - float(row["total_cost"])
                    for row in order_rows
                    if row["trade_date"] == trade_date and row["symbol"] == symbol
                )
                + remaining_quantity * (close_price - entry_price)
            )
            same_day_loss_avoided = round(simulated_pnl - baseline_hold_pnl, 4)
            total_same_day_loss_avoided += same_day_loss_avoided

            session_rows.append(
                {
                    "trade_date": trade_date,
                    "month_bucket": hit_row["month_bucket"],
                    "symbol": symbol,
                    "predicted_tier": hit_row["predicted_tier"],
                    "entry_price": round(entry_price, 4),
                    "reference_quantity": quantity,
                    "reference_notional": round(quantity * entry_price, 4),
                    "first_reversal_minute": onsets["reversal_watch"] or "",
                    "first_severe_minute": onsets["severe_override_positive"] or "",
                    "filled_step_count": filled_steps,
                    "remaining_quantity_after_sim": remaining_quantity,
                    "close_price": round(close_price, 4),
                    "baseline_hold_pnl": round(baseline_hold_pnl, 4),
                    "simulated_pnl": round(simulated_pnl, 4),
                    "same_day_loss_avoided": same_day_loss_avoided,
                    "simulated_close_value": round(simulated_close_value, 4),
                }
            )

        self.output_sessions_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_sessions_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)
        with self.output_orders_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(order_rows[0].keys()))
            writer.writeheader()
            writer.writerows(order_rows)

        summary = {
            "acceptance_posture": "build_v134l_commercial_aerospace_intraday_broader_hit_simulator_v1",
            "broader_hit_session_count": len(session_rows),
            "reference_notional_per_session": self.reference_notional,
            "simulated_order_count": len(order_rows),
            "reversal_execution_count": reversal_execution_count,
            "severe_execution_count": severe_execution_count,
            "pending_out_of_window_count": pending_out_of_window_count,
            "zero_quantity_session_count": zero_quantity_session_count,
            "same_day_loss_avoided_total": round(total_same_day_loss_avoided, 4),
            "session_csv": str(self.output_sessions_csv.relative_to(self.repo_root)),
            "orders_csv": str(self.output_orders_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_intraday_broader_hit_simulator_ready_for_phase_2_guarded_triage",
        }
        acceptance_rows = [
            {
                "acceptance_item": "broader_hit_scope_only",
                "status": "pass" if len(session_rows) == 24 else "fail",
                "detail": f"broader_hit_session_count = {len(session_rows)}",
            },
            {
                "acceptance_item": "no_mild_execution",
                "status": "pass",
                "detail": "Only reversal and severe trigger tiers are executable in the broader-hit phase-2 lane.",
            },
            {
                "acceptance_item": "out_of_window_explicit",
                "status": "pass",
                "detail": f"pending_out_of_window_count = {pending_out_of_window_count}",
            },
        ]
        interpretation = [
            "V1.34L widens phase 2 from the six canonical seeds to the already-flagged broader-hit sessions under a normalized reference-notional shadow simulator.",
            "The widening still stays inside phase 2: only reversal and severe are executable, mild remains governance-only, and no replay binding is attempted.",
        ]
        return V134LCommercialAerospaceIntradayBroaderHitSimulatorReport(
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
    result: V134LCommercialAerospaceIntradayBroaderHitSimulatorReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LCommercialAerospaceIntradayBroaderHitSimulatorAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134l_commercial_aerospace_intraday_broader_hit_simulator_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
