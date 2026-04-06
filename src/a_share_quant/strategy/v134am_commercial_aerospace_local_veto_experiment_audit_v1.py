from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v132u_commercial_aerospace_local_1min_state_transition_audit_v1 import _symbol_to_archive_member
from a_share_quant.strategy.v134c_commercial_aerospace_intraday_seed_simulator_v1 import _calc_costs
from a_share_quant.strategy.v134l_commercial_aerospace_intraday_broader_hit_simulator_v1 import _round_lot_quantity


def _rounded_half(quantity: int) -> int:
    if quantity <= 0:
        return 0
    lot = ((quantity // 2) // 100) * 100
    if lot <= 0:
        lot = min(100, quantity)
    return min(lot, quantity)


@dataclass(slots=True)
class V134AMCommercialAerospaceLocalVetoExperimentAuditV1Report:
    summary: dict[str, Any]
    impacted_rows: list[dict[str, Any]]
    compare_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "impacted_rows": self.impacted_rows,
            "compare_rows": self.compare_rows,
            "interpretation": self.interpretation,
        }


class V134AMCommercialAerospaceLocalVetoExperimentAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.local_veto_path = (
            repo_root / "reports" / "analysis" / "v134ak_commercial_aerospace_rebound_cost_local_veto_audit_v1.json"
        )
        self.hits_csv = repo_root / "data" / "training" / "commercial_aerospace_local_1min_session_expansion_hits_v1.csv"
        self.daily_bars_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.reference_notional = 100000.0
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_local_veto_experiment_audit_v1.csv"
        )

    def _load_target_rows(self) -> list[dict[str, Any]]:
        payload = json.loads(self.local_veto_path.read_text(encoding="utf-8"))
        return payload["matched_rows"]

    def _load_hit_map(self) -> dict[tuple[str, str], dict[str, Any]]:
        with self.hits_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            return {(row["trade_date"], row["symbol"]): row for row in csv.DictReader(handle)}

    def _load_session_rows(self, trade_date: str, symbol: str) -> list[dict[str, Any]]:
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
            }
            for idx, row in enumerate(raw_rows, start=1)
        ]

    def _load_daily_close_map(self) -> dict[str, list[tuple[str, float]]]:
        close_map: dict[str, list[tuple[str, float]]] = {}
        with self.daily_bars_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                close_map.setdefault(row["symbol"], []).append((row["trade_date"], float(row["close"])))
        for symbol in close_map:
            close_map[symbol].sort(key=lambda item: item[0])
        return close_map

    @staticmethod
    def _future_close(close_rows: list[tuple[str, float]], trade_date: str, horizon_days: int) -> float | None:
        dates = [d for d, _ in close_rows]
        if trade_date not in dates:
            return None
        idx = dates.index(trade_date)
        target_idx = idx + horizon_days
        if target_idx >= len(close_rows):
            return None
        return close_rows[target_idx][1]

    @staticmethod
    def _positive_rebound_cost(sell_quantity: int, sell_price: float, future_close: float | None) -> float:
        if future_close is None:
            return 0.0
        return round(max(0.0, sell_quantity * (future_close - sell_price)), 4)

    def analyze(self) -> V134AMCommercialAerospaceLocalVetoExperimentAuditV1Report:
        hit_map = self._load_hit_map()
        target_rows = self._load_target_rows()
        close_map = self._load_daily_close_map()

        impacted_rows: list[dict[str, Any]] = []
        total_same_day_delta = 0.0
        total_rebound_cost_saved = 0.0

        for target in target_rows:
            trade_date = target["trade_date"]
            symbol = target["symbol"]
            hit_row = hit_map[(trade_date, symbol)]
            session_rows = self._load_session_rows(trade_date, symbol)
            entry_price = float(session_rows[0]["open_px"])
            quantity = _round_lot_quantity(entry_price, self.reference_notional)
            baseline_hold_pnl = quantity * (float(session_rows[-1]["close_px"]) - entry_price)

            reversal_minute = int(target["reversal_minute"])
            reversal_fill_row = session_rows[reversal_minute]
            reversal_fill_price = float(reversal_fill_row["open_px"])

            current_simulated_pnl = quantity * (reversal_fill_price - entry_price) - _calc_costs(
                quantity * reversal_fill_price, action="sell"
            )["total_cost"]
            current_same_day_loss_avoided = round(current_simulated_pnl - baseline_hold_pnl, 4)

            adjusted_reversal_qty = _rounded_half(quantity)
            adjusted_remaining = quantity - adjusted_reversal_qty
            adjusted_reversal_notional = adjusted_reversal_qty * reversal_fill_price
            adjusted_reversal_pnl = adjusted_reversal_qty * (reversal_fill_price - entry_price) - _calc_costs(
                adjusted_reversal_notional, action="sell"
            )["total_cost"]

            severe_fill_price = None
            severe_qty = 0
            severe_minute_raw = hit_row.get("first_severe_minute", "")
            if severe_minute_raw:
                severe_minute = int(severe_minute_raw)
                if severe_minute + 1 <= len(session_rows):
                    severe_fill_row = session_rows[severe_minute]
                    severe_fill_price = float(severe_fill_row["open_px"])
                    severe_qty = adjusted_remaining

            adjusted_simulated_pnl = adjusted_reversal_pnl
            if severe_qty > 0 and severe_fill_price is not None:
                adjusted_simulated_pnl += severe_qty * (severe_fill_price - entry_price) - _calc_costs(
                    severe_qty * severe_fill_price, action="sell"
                )["total_cost"]
                adjusted_remaining = 0
            else:
                adjusted_simulated_pnl += adjusted_remaining * (float(session_rows[-1]["close_px"]) - entry_price)

            adjusted_same_day_loss_avoided = round(adjusted_simulated_pnl - baseline_hold_pnl, 4)

            future_close_5d = self._future_close(close_map.get(symbol, []), trade_date, 5)
            current_rebound_cost_5d = self._positive_rebound_cost(quantity, reversal_fill_price, future_close_5d)
            adjusted_rebound_cost_5d = self._positive_rebound_cost(
                adjusted_reversal_qty, reversal_fill_price, future_close_5d
            )
            if severe_qty > 0 and severe_fill_price is not None:
                adjusted_rebound_cost_5d += self._positive_rebound_cost(severe_qty, severe_fill_price, future_close_5d)
            rebound_cost_saved_5d = round(current_rebound_cost_5d - adjusted_rebound_cost_5d, 4)

            same_day_delta = round(adjusted_same_day_loss_avoided - current_same_day_loss_avoided, 4)
            total_same_day_delta += same_day_delta
            total_rebound_cost_saved += rebound_cost_saved_5d

            impacted_rows.append(
                {
                    "trade_date": trade_date,
                    "symbol": symbol,
                    "current_same_day_loss_avoided": current_same_day_loss_avoided,
                    "adjusted_same_day_loss_avoided": adjusted_same_day_loss_avoided,
                    "same_day_delta": same_day_delta,
                    "current_rebound_cost_5d": current_rebound_cost_5d,
                    "adjusted_rebound_cost_5d": adjusted_rebound_cost_5d,
                    "rebound_cost_saved_5d": rebound_cost_saved_5d,
                    "severe_follow_on_used": bool(severe_qty > 0),
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(impacted_rows[0].keys()))
            writer.writeheader()
            writer.writerows(impacted_rows)

        compare_rows = [
            {
                "variant": "current_full_reversal_reference",
                "same_day_loss_avoided_delta": 0.0,
                "rebound_cost_saved_5d": 0.0,
            },
            {
                "variant": "local_veto_experiment_reversal_50pct_on_matched_cases",
                "same_day_loss_avoided_delta": round(total_same_day_delta, 4),
                "rebound_cost_saved_5d": round(total_rebound_cost_saved, 4),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134am_commercial_aerospace_local_veto_experiment_audit_v1",
            "impacted_session_count": len(impacted_rows),
            "same_day_loss_avoided_delta_total": round(total_same_day_delta, 4),
            "rebound_cost_saved_5d_total": round(total_rebound_cost_saved, 4),
            "impact_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_local_veto_experiment_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AM runs the first local veto experiment inside the current wider phase-2 reference.",
            "It only touches the two matched rebound-cost cases and downgrades full reversal to partial reversal there, while leaving the broader surface and all other sessions unchanged.",
        ]
        return V134AMCommercialAerospaceLocalVetoExperimentAuditV1Report(
            summary=summary,
            impacted_rows=impacted_rows,
            compare_rows=compare_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AMCommercialAerospaceLocalVetoExperimentAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AMCommercialAerospaceLocalVetoExperimentAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134am_commercial_aerospace_local_veto_experiment_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
