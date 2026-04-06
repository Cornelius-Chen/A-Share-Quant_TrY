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
from a_share_quant.strategy.v134l_commercial_aerospace_intraday_broader_hit_simulator_v1 import _round_lot_quantity


@dataclass(slots=True)
class V134AOCommercialAerospaceLocalReversalDeferralAuditV1Report:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    impacted_rows: list[dict[str, Any]]
    compare_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "impacted_rows": self.impacted_rows,
            "compare_rows": self.compare_rows,
            "interpretation": self.interpretation,
        }


class V134AOCommercialAerospaceLocalReversalDeferralAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.local_veto_path = analysis_dir / "v134ak_commercial_aerospace_rebound_cost_local_veto_audit_v1.json"
        self.hits_csv = repo_root / "data" / "training" / "commercial_aerospace_local_1min_session_expansion_hits_v1.csv"
        self.daily_bars_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.reference_notional = 100000.0
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_local_reversal_deferral_audit_v1.csv"
        )

    def _load_target_rows(self) -> list[dict[str, Any]]:
        payload = json.loads(self.local_veto_path.read_text(encoding="utf-8"))
        return payload["matched_rows"]

    def _load_session_rows(self, trade_date: str, symbol: str) -> list[dict[str, Any]]:
        zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
        member_name = _symbol_to_archive_member(symbol)
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open(member_name, "r") as member:
                raw_rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]
        rows: list[dict[str, Any]] = []
        highs: list[float] = []
        lows: list[float] = []
        base_open = float(raw_rows[0][3])
        for idx, row in enumerate(raw_rows, start=1):
            open_px = float(row[3])
            close_px = float(row[4])
            high_px = float(row[5])
            low_px = float(row[6])
            highs.append(high_px)
            lows.append(low_px)
            high_so_far = max(highs)
            low_so_far = min(lows)
            close_location = 0.5 if high_so_far == low_so_far else (close_px - low_so_far) / (high_so_far - low_so_far)
            state = _running_state(
                current_return=close_px / base_open - 1.0,
                drawdown=low_so_far / base_open - 1.0,
                close_location=close_location,
            )
            rows.append(
                {
                    "minute_index": idx,
                    "timestamp": row[0],
                    "open_px": open_px,
                    "close_px": close_px,
                    "state": state,
                }
            )
        return rows

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

    @staticmethod
    def _find_deferred_reversal_minute(
        session_rows: list[dict[str, Any]],
        *,
        first_reversal_minute: int,
        neutral_streak_len: int,
        gap_minute: int,
    ) -> int | None:
        scan_idx = first_reversal_minute + 1
        while scan_idx <= len(session_rows) and session_rows[scan_idx - 1]["state"] == "reversal_watch":
            scan_idx += 1

        neutral_start: int | None = None
        neutral_count = 0
        for idx in range(scan_idx, len(session_rows) + 1):
            state = session_rows[idx - 1]["state"]
            if state == "neutral":
                neutral_count += 1
                if neutral_start is None:
                    neutral_start = idx
                if neutral_count >= neutral_streak_len:
                    break
            elif state == "reversal_watch":
                return None
            else:
                neutral_start = None
                neutral_count = 0
        if neutral_start is None or neutral_count < neutral_streak_len:
            return None

        search_start = neutral_start + neutral_count
        for idx in range(search_start, len(session_rows) + 1):
            state = session_rows[idx - 1]["state"]
            if state == "severe_override_positive":
                return idx
            if state == "reversal_watch" and idx - first_reversal_minute >= gap_minute:
                return idx
        return None

    def analyze(self) -> V134AOCommercialAerospaceLocalReversalDeferralAuditV1Report:
        target_rows = self._load_target_rows()
        close_map = self._load_daily_close_map()

        candidate_specs = [
            {"neutral_streak_len": 2, "gap_minute": 8},
            {"neutral_streak_len": 2, "gap_minute": 10},
            {"neutral_streak_len": 2, "gap_minute": 12},
            {"neutral_streak_len": 3, "gap_minute": 8},
            {"neutral_streak_len": 3, "gap_minute": 10},
        ]

        variant_rows: list[dict[str, Any]] = []
        matched_case_rows: dict[tuple[int, int], list[dict[str, Any]]] = {}

        for spec in candidate_specs:
            same_day_delta_total = 0.0
            rebound_saved_total = 0.0
            impacted_case_count = 0
            case_rows: list[dict[str, Any]] = []
            for target in target_rows:
                trade_date = target["trade_date"]
                symbol = target["symbol"]
                first_reversal_minute = int(target["reversal_minute"])
                session_rows = self._load_session_rows(trade_date, symbol)
                deferred_minute = self._find_deferred_reversal_minute(
                    session_rows,
                    first_reversal_minute=first_reversal_minute,
                    neutral_streak_len=spec["neutral_streak_len"],
                    gap_minute=spec["gap_minute"],
                )
                if deferred_minute is None:
                    continue

                entry_price = float(session_rows[0]["open_px"])
                quantity = _round_lot_quantity(entry_price, self.reference_notional)
                baseline_hold_pnl = quantity * (float(session_rows[-1]["close_px"]) - entry_price)

                current_fill_price = float(session_rows[first_reversal_minute]["open_px"])
                current_simulated_pnl = quantity * (current_fill_price - entry_price) - _calc_costs(
                    quantity * current_fill_price, action="sell"
                )["total_cost"]
                current_same_day_loss_avoided = round(current_simulated_pnl - baseline_hold_pnl, 4)

                adjusted_fill_price = float(session_rows[deferred_minute]["open_px"])
                adjusted_simulated_pnl = quantity * (adjusted_fill_price - entry_price) - _calc_costs(
                    quantity * adjusted_fill_price, action="sell"
                )["total_cost"]
                adjusted_same_day_loss_avoided = round(adjusted_simulated_pnl - baseline_hold_pnl, 4)
                same_day_delta = round(adjusted_same_day_loss_avoided - current_same_day_loss_avoided, 4)

                future_close_5d = self._future_close(close_map.get(symbol, []), trade_date, 5)
                current_rebound_cost_5d = self._positive_rebound_cost(quantity, current_fill_price, future_close_5d)
                adjusted_rebound_cost_5d = self._positive_rebound_cost(quantity, adjusted_fill_price, future_close_5d)
                rebound_saved_5d = round(current_rebound_cost_5d - adjusted_rebound_cost_5d, 4)

                same_day_delta_total += same_day_delta
                rebound_saved_total += rebound_saved_5d
                impacted_case_count += 1
                case_rows.append(
                    {
                        "trade_date": trade_date,
                        "symbol": symbol,
                        "first_reversal_minute": first_reversal_minute,
                        "deferred_trigger_minute": deferred_minute,
                        "current_fill_price": round(current_fill_price, 4),
                        "adjusted_fill_price": round(adjusted_fill_price, 4),
                        "same_day_delta": same_day_delta,
                        "rebound_cost_saved_5d": rebound_saved_5d,
                    }
                )

            variant_rows.append(
                {
                    "neutral_streak_len": spec["neutral_streak_len"],
                    "gap_minute": spec["gap_minute"],
                    "impacted_case_count": impacted_case_count,
                    "same_day_loss_avoided_delta_total": round(same_day_delta_total, 4),
                    "rebound_cost_saved_5d_total": round(rebound_saved_total, 4),
                }
            )
            matched_case_rows[(spec["neutral_streak_len"], spec["gap_minute"])] = case_rows

        best_row = max(
            variant_rows,
            key=lambda row: (
                row["same_day_loss_avoided_delta_total"] > 0,
                row["same_day_loss_avoided_delta_total"],
                row["rebound_cost_saved_5d_total"],
                row["gap_minute"],
            ),
        )
        best_key = (int(best_row["neutral_streak_len"]), int(best_row["gap_minute"]))
        impacted_rows = matched_case_rows[best_key]

        compare_rows = [
            {
                "variant": "current_full_reversal_reference",
                "same_day_loss_avoided_delta_total": 0.0,
                "rebound_cost_saved_5d_total": 0.0,
            },
            {
                "variant": "local_reversal_deferral_best_variant",
                "same_day_loss_avoided_delta_total": best_row["same_day_loss_avoided_delta_total"],
                "rebound_cost_saved_5d_total": best_row["rebound_cost_saved_5d_total"],
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(variant_rows[0].keys()))
            writer.writeheader()
            writer.writerows(variant_rows)

        summary = {
            "acceptance_posture": "freeze_v134ao_commercial_aerospace_local_reversal_deferral_audit_v1",
            "variant_count": len(variant_rows),
            "best_neutral_streak_len": best_row["neutral_streak_len"],
            "best_gap_minute": best_row["gap_minute"],
            "best_impacted_case_count": best_row["impacted_case_count"],
            "best_same_day_loss_avoided_delta_total": best_row["same_day_loss_avoided_delta_total"],
            "best_rebound_cost_saved_5d_total": best_row["rebound_cost_saved_5d_total"],
            "variant_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_local_reversal_deferral_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AO audits a narrower local expression for rebound-cost cases than simple partial selling.",
            "It only defers the first full reversal when the initial reversal is followed by a clean neutral reclaim before any re-entry into reversal, then exits on the next reversal or severe trigger.",
        ]
        return V134AOCommercialAerospaceLocalReversalDeferralAuditV1Report(
            summary=summary,
            variant_rows=variant_rows,
            impacted_rows=impacted_rows,
            compare_rows=compare_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AOCommercialAerospaceLocalReversalDeferralAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AOCommercialAerospaceLocalReversalDeferralAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ao_commercial_aerospace_local_reversal_deferral_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
