from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


COMMISSION_RATE = 0.0003
MIN_COMMISSION = 5.0
STAMP_TAX_RATE = 0.001
SLIPPAGE_BPS = 5.0


@dataclass(slots=True)
class V134CBCommercialAerospaceIsolatedSellSideShadowLaneV1Report:
    summary: dict[str, Any]
    session_rows: list[dict[str, Any]]
    order_rows: list[dict[str, Any]]
    reconciliation_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "session_rows": self.session_rows,
            "order_rows": self.order_rows,
            "reconciliation_rows": self.reconciliation_rows,
            "interpretation": self.interpretation,
        }


class V134CBCommercialAerospaceIsolatedSellSideShadowLaneV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.sessions_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_broader_hit_simulator_sessions_v1.csv"
        )
        self.base_orders_path = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_broader_hit_simulator_orders_v1.csv"
        )
        self.ledger_path = (
            repo_root / "reports" / "analysis" / "v134bz_commercial_aerospace_start_of_day_holdings_ledger_v1.json"
        )
        self.deferral_path = (
            repo_root / "reports" / "analysis" / "v134ao_commercial_aerospace_local_reversal_deferral_audit_v1.json"
        )
        self.orders_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_isolated_sell_side_shadow_lane_orders_v1.csv"
        )
        self.sessions_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_isolated_sell_side_shadow_lane_sessions_v1.csv"
        )
        self.reconciliation_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_isolated_sell_side_shadow_lane_reconciliation_v1.csv"
        )

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, str]]:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def _commission(notional: float) -> float:
        return max(notional * COMMISSION_RATE, MIN_COMMISSION)

    def analyze(self) -> V134CBCommercialAerospaceIsolatedSellSideShadowLaneV1Report:
        sessions = self._load_csv(self.sessions_path)
        base_orders = self._load_csv(self.base_orders_path)
        ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        deferral = json.loads(self.deferral_path.read_text(encoding="utf-8"))

        ledger_by_key = {
            (row["trade_date"], row["symbol"]): row
            for row in ledger["ledger_rows"]
        }
        base_order_by_key = {
            (row["trade_date"], row["symbol"], row["trigger_tier"]): row
            for row in base_orders
        }
        deferral_override = {
            (row["trade_date"], row["symbol"]): row
            for row in deferral["impacted_rows"]
        }

        session_rows: list[dict[str, Any]] = []
        order_rows: list[dict[str, Any]] = []
        reconciliation_rows: list[dict[str, Any]] = []

        for session in sessions:
            key = (session["trade_date"], session["symbol"])
            ledger_row = ledger_by_key.get(
                key,
                {
                    "trade_date": session["trade_date"],
                    "symbol": session["symbol"],
                    "start_of_day_quantity": 0,
                    "eligible_intraday_sell_quantity": 0,
                    "same_day_open_quantity": 0,
                    "same_day_add_quantity": 0,
                    "same_day_new_lots_quantity": 0,
                    "same_day_reduce_quantity": 0,
                    "same_day_close_quantity": 0,
                    "end_of_day_quantity_without_intraday": 0,
                    "has_same_day_primary_action": False,
                },
            )
            predicted_tier = session["predicted_tier"]
            eligible_qty = int(ledger_row["eligible_intraday_sell_quantity"])
            same_day_new_lots_qty = int(ledger_row["same_day_new_lots_quantity"])
            same_day_reduce_qty = int(ledger_row["same_day_reduce_quantity"])
            same_day_close_qty = int(ledger_row["same_day_close_quantity"])
            start_qty = int(ledger_row["start_of_day_quantity"])

            lane_status = "skipped"
            skip_reason = ""
            trigger_tier = ""
            trigger_minute = None
            fill_minute = None
            fill_price = None
            sell_quantity = 0
            protected_mark_to_close = 0.0
            total_cost = 0.0

            if eligible_qty <= 0:
                skip_reason = "no_eligible_start_of_day_inventory"
            elif predicted_tier == "mild_override_watch":
                skip_reason = "mild_is_governance_only"
            else:
                reversal_minute = int(session["first_reversal_minute"]) if session["first_reversal_minute"] else None
                severe_minute = int(session["first_severe_minute"]) if session["first_severe_minute"] else None

                if predicted_tier == "reversal_watch":
                    trigger_tier = "reversal_watch"
                    if key in deferral_override:
                        trigger_minute = int(deferral_override[key]["deferred_trigger_minute"])
                        fill_minute = trigger_minute + 1
                        fill_price = float(deferral_override[key]["adjusted_fill_price"])
                    else:
                        trigger_minute = reversal_minute
                        base_row = base_order_by_key[(session["trade_date"], session["symbol"], "reversal_watch")]
                        fill_minute = int(base_row["fill_minute"])
                        fill_price = float(base_row["fill_price"])
                else:
                    reversal_first = reversal_minute is not None and (
                        severe_minute is None or reversal_minute <= severe_minute
                    )
                    trigger_tier = "reversal_watch" if reversal_first else "severe_override_positive"
                    base_row = base_order_by_key[(session["trade_date"], session["symbol"], trigger_tier)]
                    trigger_minute = int(base_row["trigger_minute"])
                    fill_minute = int(base_row["fill_minute"])
                    fill_price = float(base_row["fill_price"])

                sell_quantity = eligible_qty
                sell_notional = round(fill_price * sell_quantity, 4)
                commission = round(self._commission(sell_notional), 4)
                stamp_tax = round(sell_notional * STAMP_TAX_RATE, 4)
                slippage = round(sell_notional * SLIPPAGE_BPS / 10000.0, 4)
                total_cost = round(commission + stamp_tax + slippage, 4)
                close_price = float(session["close_price"])
                protected_mark_to_close = round((fill_price - close_price) * sell_quantity - total_cost, 4)
                lane_status = "executed"

                order_rows.append(
                    {
                        "trade_date": session["trade_date"],
                        "symbol": session["symbol"],
                        "predicted_tier": predicted_tier,
                        "trigger_tier": trigger_tier,
                        "trigger_minute": trigger_minute,
                        "fill_minute": fill_minute,
                        "fill_price": fill_price,
                        "sell_quantity": sell_quantity,
                        "sell_notional": sell_notional,
                        "commission": commission,
                        "stamp_tax": stamp_tax,
                        "slippage": slippage,
                        "total_cost": total_cost,
                        "close_price": close_price,
                        "protected_mark_to_close": protected_mark_to_close,
                    }
                )

            residual_after_intraday = max(start_qty - sell_quantity, 0)
            eod_reduce_close_requested = same_day_reduce_qty + same_day_close_qty
            eod_reduce_close_effective = min(eod_reduce_close_requested, residual_after_intraday)
            eod_reduce_close_clipped = max(eod_reduce_close_requested - residual_after_intraday, 0)
            reconciliation_rows.append(
                {
                    "trade_date": session["trade_date"],
                    "symbol": session["symbol"],
                    "start_of_day_quantity": start_qty,
                    "same_day_new_lots_quantity": same_day_new_lots_qty,
                    "intraday_sell_quantity": sell_quantity,
                    "residual_carried_quantity_after_intraday": residual_after_intraday,
                    "same_day_reduce_close_requested": eod_reduce_close_requested,
                    "same_day_reduce_close_effective": eod_reduce_close_effective,
                    "same_day_reduce_close_clipped": eod_reduce_close_clipped,
                    "same_day_new_lots_protected": same_day_new_lots_qty,
                }
            )

            session_rows.append(
                {
                    "trade_date": session["trade_date"],
                    "symbol": session["symbol"],
                    "predicted_tier": predicted_tier,
                    "start_of_day_quantity": start_qty,
                    "eligible_intraday_sell_quantity": eligible_qty,
                    "same_day_new_lots_quantity": same_day_new_lots_qty,
                    "lane_status": lane_status,
                    "skip_reason": skip_reason,
                    "trigger_tier": trigger_tier,
                    "sell_quantity": sell_quantity,
                    "protected_mark_to_close": protected_mark_to_close,
                    "same_day_reduce_close_clipped": eod_reduce_close_clipped,
                }
            )

        for path, rows in (
            (self.sessions_csv, session_rows),
            (self.orders_csv, order_rows),
            (self.reconciliation_csv, reconciliation_rows),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        summary = {
            "acceptance_posture": "build_v134cb_commercial_aerospace_isolated_sell_side_shadow_lane_v1",
            "current_reference": "broader_hit_current_plus_reversal_100pct_plus_local_reversal_deferral",
            "broader_hit_session_count": len(session_rows),
            "executed_session_count": sum(1 for row in session_rows if row["lane_status"] == "executed"),
            "skipped_no_inventory_count": sum(
                1 for row in session_rows if row["skip_reason"] == "no_eligible_start_of_day_inventory"
            ),
            "skipped_mild_count": sum(1 for row in session_rows if row["skip_reason"] == "mild_is_governance_only"),
            "order_count": len(order_rows),
            "total_protected_mark_to_close": round(sum(row["protected_mark_to_close"] for row in order_rows), 4),
            "clipped_reconciliation_count": sum(
                1 for row in reconciliation_rows if row["same_day_reduce_close_clipped"] > 0
            ),
            "orders_csv": str(self.orders_csv.relative_to(self.repo_root)),
            "sessions_csv": str(self.sessions_csv.relative_to(self.repo_root)),
            "reconciliation_csv": str(self.reconciliation_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_isolated_sell_side_shadow_lane_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34CB instantiates the first isolated sell-side shadow lane using only carried start-of-day inventory from the frozen EOD primary.",
            "The lane protects same-day new lots, executes only sell-side minute triggers, and emits explicit reconciliation rows when later EOD reduce/close actions would overconsume residual carried inventory.",
        ]
        return V134CBCommercialAerospaceIsolatedSellSideShadowLaneV1Report(
            summary=summary,
            session_rows=session_rows,
            order_rows=order_rows,
            reconciliation_rows=reconciliation_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CBCommercialAerospaceIsolatedSellSideShadowLaneV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CBCommercialAerospaceIsolatedSellSideShadowLaneV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cb_commercial_aerospace_isolated_sell_side_shadow_lane_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
