from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CFCommercialAerospaceIsolatedSellSideHorizonQualityAuditV1Report:
    summary: dict[str, Any]
    horizon_rows: list[dict[str, Any]]
    session_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "horizon_rows": self.horizon_rows,
            "session_rows": self.session_rows,
            "interpretation": self.interpretation,
        }


class V134CFCommercialAerospaceIsolatedSellSideHorizonQualityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.orders_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_isolated_sell_side_shadow_lane_orders_v1.csv"
        )
        self.daily_bars_csv = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_isolated_sell_side_horizon_quality_audit_v1.csv"
        )

    def _load_orders(self) -> list[dict[str, str]]:
        with self.orders_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def _load_daily_close_map(self) -> dict[str, list[tuple[str, float]]]:
        close_map: dict[str, list[tuple[str, float]]] = {}
        with self.daily_bars_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                symbol = row["symbol"]
                close_map.setdefault(symbol, []).append((row["trade_date"], float(row["close"])))
        for symbol in close_map:
            close_map[symbol].sort(key=lambda item: item[0])
        return close_map

    @staticmethod
    def _future_close(close_rows: list[tuple[str, float]], trade_date: str, horizon_days: int) -> float | None:
        dates = [trade_date_ for trade_date_, _ in close_rows]
        if trade_date not in dates:
            return None
        idx = dates.index(trade_date)
        target_idx = idx + horizon_days
        if target_idx >= len(close_rows):
            return None
        return close_rows[target_idx][1]

    def analyze(self) -> V134CFCommercialAerospaceIsolatedSellSideHorizonQualityAuditV1Report:
        orders = self._load_orders()
        close_map = self._load_daily_close_map()
        session_rows: list[dict[str, Any]] = []

        for order in orders:
            symbol = order["symbol"]
            trade_date = order["trade_date"]
            fill_price = float(order["fill_price"])
            sell_quantity = int(order["sell_quantity"])
            symbol_closes = close_map.get(symbol, [])
            future_1d = self._future_close(symbol_closes, trade_date, 1)
            future_3d = self._future_close(symbol_closes, trade_date, 3)
            future_5d = self._future_close(symbol_closes, trade_date, 5)

            session_rows.append(
                {
                    "trade_date": trade_date,
                    "symbol": symbol,
                    "predicted_tier": order["predicted_tier"],
                    "trigger_tier": order["trigger_tier"],
                    "fill_price": round(fill_price, 4),
                    "sell_quantity": sell_quantity,
                    "same_day_protected_mark_to_close": round(float(order["protected_mark_to_close"]), 4),
                    "horizon_pnl_if_held_1d": round(sell_quantity * (future_1d - fill_price), 4)
                    if future_1d is not None
                    else "",
                    "horizon_pnl_if_held_3d": round(sell_quantity * (future_3d - fill_price), 4)
                    if future_3d is not None
                    else "",
                    "horizon_pnl_if_held_5d": round(sell_quantity * (future_5d - fill_price), 4)
                    if future_5d is not None
                    else "",
                }
            )

        horizon_rows: list[dict[str, Any]] = []
        for horizon in (1, 3, 5):
            key = f"horizon_pnl_if_held_{horizon}d"
            numeric = [float(row[key]) for row in session_rows if row[key] != ""]
            positive = [value for value in numeric if value > 0]
            negative = [value for value in numeric if value < 0]
            horizon_rows.append(
                {
                    "horizon_days": horizon,
                    "session_count": len(numeric),
                    "net_horizon_pnl_if_held": round(sum(numeric), 4),
                    "positive_rebound_cost_count": len(positive),
                    "positive_rebound_cost_total": round(sum(positive), 4),
                    "negative_followthrough_benefit_count": len(negative),
                    "negative_followthrough_benefit_total": round(sum(negative), 4),
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        row_1d = next(row for row in horizon_rows if row["horizon_days"] == 1)
        row_3d = next(row for row in horizon_rows if row["horizon_days"] == 3)
        row_5d = next(row for row in horizon_rows if row["horizon_days"] == 5)
        summary = {
            "acceptance_posture": "freeze_v134cf_commercial_aerospace_isolated_sell_side_horizon_quality_audit_v1",
            "executed_order_count": len(session_rows),
            "same_day_protected_mark_to_close_total": round(
                sum(float(row["same_day_protected_mark_to_close"]) for row in session_rows),
                4,
            ),
            "net_horizon_pnl_if_held_1d": row_1d["net_horizon_pnl_if_held"],
            "net_horizon_pnl_if_held_3d": row_3d["net_horizon_pnl_if_held"],
            "net_horizon_pnl_if_held_5d": row_5d["net_horizon_pnl_if_held"],
            "session_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_isolated_sell_side_horizon_quality_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34CF checks whether the first isolated sell-side binding surface still makes sense beyond same-day close.",
            "It does not reopen replay; it only asks whether the holdings-aware sell lane mostly protects followthrough downside or instead mainly pays rebound-cost after the intraday exits.",
        ]
        return V134CFCommercialAerospaceIsolatedSellSideHorizonQualityAuditV1Report(
            summary=summary,
            horizon_rows=horizon_rows,
            session_rows=session_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CFCommercialAerospaceIsolatedSellSideHorizonQualityAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CFCommercialAerospaceIsolatedSellSideHorizonQualityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cf_commercial_aerospace_isolated_sell_side_horizon_quality_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
