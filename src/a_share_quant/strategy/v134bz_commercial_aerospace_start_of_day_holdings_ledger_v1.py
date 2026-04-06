from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BZCommercialAerospaceStartOfDayHoldingsLedgerV1Report:
    summary: dict[str, Any]
    ledger_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "ledger_rows": self.ledger_rows,
            "interpretation": self.interpretation,
        }


class V134BZCommercialAerospaceStartOfDayHoldingsLedgerV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.primary_orders_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        )
        self.daily_state_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_daily_state_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_start_of_day_holdings_ledger_v1.csv"
        )

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, str]]:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V134BZCommercialAerospaceStartOfDayHoldingsLedgerV1Report:
        primary_orders = self._load_csv(self.primary_orders_path)
        daily_state_rows = self._load_csv(self.daily_state_path)

        orders_by_date: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in primary_orders:
            orders_by_date[row["execution_trade_date"]].append(row)

        all_dates = sorted({row["trade_date"] for row in daily_state_rows} | set(orders_by_date))
        holdings: dict[str, int] = defaultdict(int)
        ledger_rows: list[dict[str, Any]] = []

        for trade_date in all_dates:
            same_day_orders = orders_by_date.get(trade_date, [])
            same_day_symbols = {row["symbol"] for row in same_day_orders}
            carried_symbols = {symbol for symbol, quantity in holdings.items() if quantity != 0}
            symbols = sorted(carried_symbols | same_day_symbols)
            if not symbols:
                continue

            action_buckets: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
            for row in same_day_orders:
                quantity = int(float(row["quantity"]))
                action_buckets[row["symbol"]][row["action"]] += quantity

            for symbol in symbols:
                start_of_day_quantity = holdings.get(symbol, 0)
                open_quantity = action_buckets[symbol].get("open", 0)
                add_quantity = action_buckets[symbol].get("add", 0)
                reduce_quantity = action_buckets[symbol].get("reduce", 0)
                close_quantity = action_buckets[symbol].get("close", 0)
                same_day_new_lots_quantity = open_quantity + add_quantity
                eligible_intraday_sell_quantity = max(start_of_day_quantity, 0)
                end_of_day_quantity_without_intraday = (
                    start_of_day_quantity + same_day_new_lots_quantity - reduce_quantity - close_quantity
                )

                ledger_rows.append(
                    {
                        "trade_date": trade_date,
                        "symbol": symbol,
                        "start_of_day_quantity": start_of_day_quantity,
                        "eligible_intraday_sell_quantity": eligible_intraday_sell_quantity,
                        "same_day_open_quantity": open_quantity,
                        "same_day_add_quantity": add_quantity,
                        "same_day_new_lots_quantity": same_day_new_lots_quantity,
                        "same_day_reduce_quantity": reduce_quantity,
                        "same_day_close_quantity": close_quantity,
                        "end_of_day_quantity_without_intraday": end_of_day_quantity_without_intraday,
                        "has_same_day_primary_action": bool(same_day_orders and symbol in same_day_symbols),
                    }
                )

            for row in same_day_orders:
                quantity = int(float(row["quantity"]))
                if row["action"] in {"open", "add"}:
                    holdings[row["symbol"]] += quantity
                elif row["action"] in {"reduce", "close"}:
                    holdings[row["symbol"]] -= quantity

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(ledger_rows[0].keys()))
            writer.writeheader()
            writer.writerows(ledger_rows)

        summary = {
            "acceptance_posture": "build_v134bz_commercial_aerospace_start_of_day_holdings_ledger_v1",
            "ledger_row_count": len(ledger_rows),
            "trade_date_count": len({row["trade_date"] for row in ledger_rows}),
            "symbol_count": len({row["symbol"] for row in ledger_rows}),
            "positive_start_of_day_row_count": sum(1 for row in ledger_rows if row["start_of_day_quantity"] > 0),
            "same_day_new_lots_row_count": sum(1 for row in ledger_rows if row["same_day_new_lots_quantity"] > 0),
            "same_day_primary_action_row_count": sum(1 for row in ledger_rows if row["has_same_day_primary_action"]),
            "ledger_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_start_of_day_holdings_ledger_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BZ builds the first real start-of-day holdings ledger from the frozen EOD primary.",
            "The ledger separates carried inventory from same-day new lots so future intraday sell binding can consume only eligible overnight quantity.",
        ]
        return V134BZCommercialAerospaceStartOfDayHoldingsLedgerV1Report(
            summary=summary,
            ledger_rows=ledger_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BZCommercialAerospaceStartOfDayHoldingsLedgerV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BZCommercialAerospaceStartOfDayHoldingsLedgerV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bz_commercial_aerospace_start_of_day_holdings_ledger_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
