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
from a_share_quant.strategy.v134l_commercial_aerospace_intraday_broader_hit_simulator_v1 import (
    _round_lot_quantity,
)


def _rounded_fractional_sell_quantity(remaining_quantity: int, fraction: float) -> int:
    if remaining_quantity <= 0:
        return 0
    raw = int(remaining_quantity * fraction)
    lot = (raw // 100) * 100
    if lot <= 0:
        lot = min(100, remaining_quantity)
    return min(lot, remaining_quantity)


@dataclass(slots=True)
class V134ACCommercialAerospaceReversalSellFractionAuditReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V134ACCommercialAerospaceReversalSellFractionAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.hit_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_local_1min_session_expansion_hits_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.reference_notional = 100000.0
        self.late_severe_cutoff_minute = 180
        self.reversal_fractions = [0.25, 0.5, 0.75, 1.0]
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reversal_sell_fraction_audit_v1.csv"
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

    def analyze(self) -> V134ACCommercialAerospaceReversalSellFractionAuditReport:
        hit_rows = self._load_hit_rows()
        variant_rows: list[dict[str, Any]] = []

        for reversal_fraction in self.reversal_fractions:
            total_same_day_loss_avoided = 0.0
            simulated_order_count = 0
            reversal_execution_count = 0
            severe_execution_count = 0
            blocked_mild_session_count = 0
            blocked_late_severe_count = 0

            for hit_row in hit_rows:
                trade_date = hit_row["trade_date"]
                symbol = hit_row["symbol"]
                predicted_tier = hit_row["predicted_tier"]
                full_session_rows = self._load_full_session_rows(trade_date, symbol)
                if not full_session_rows:
                    continue

                entry_price = float(full_session_rows[0]["open_px"])
                quantity = _round_lot_quantity(entry_price, self.reference_notional)
                if quantity <= 0:
                    continue

                close_price = float(full_session_rows[-1]["close_px"])
                baseline_hold_pnl = quantity * (close_price - entry_price)

                if predicted_tier == "mild_override_watch":
                    blocked_mild_session_count += 1
                    total_same_day_loss_avoided += 0.0
                    continue

                onsets = self._detect_state_onsets(full_session_rows)
                remaining_quantity = quantity
                simulated_pnl = 0.0
                reversal_executed = False

                ordered_trigger_specs = sorted(
                    [
                        ("reversal_watch", onsets["reversal_watch"]),
                        ("severe_override_positive", onsets["severe_override_positive"]),
                    ],
                    key=lambda item: (10**9 if item[1] is None else int(item[1])),
                )

                for trigger_tier, trigger_minute in ordered_trigger_specs:
                    if trigger_minute is None or remaining_quantity <= 0:
                        continue
                    if (
                        trigger_tier == "severe_override_positive"
                        and predicted_tier == "reversal_watch"
                        and reversal_executed
                        and int(trigger_minute) >= self.late_severe_cutoff_minute
                    ):
                        blocked_late_severe_count += 1
                        continue

                    fill_minute = int(trigger_minute) + 1
                    if fill_minute > len(full_session_rows):
                        continue

                    fill_row = full_session_rows[fill_minute - 1]
                    fill_price = float(fill_row["open_px"])
                    if trigger_tier == "reversal_watch":
                        sell_quantity = _rounded_fractional_sell_quantity(remaining_quantity, reversal_fraction)
                    else:
                        sell_quantity = remaining_quantity
                    sell_notional = sell_quantity * fill_price
                    costs = _calc_costs(sell_notional, action="sell")
                    pnl_before_cost = sell_quantity * (fill_price - entry_price)
                    simulated_pnl += pnl_before_cost - costs["total_cost"]
                    remaining_quantity -= sell_quantity
                    simulated_order_count += 1
                    if trigger_tier == "reversal_watch":
                        reversal_execution_count += 1
                        reversal_executed = True
                    else:
                        severe_execution_count += 1

                simulated_pnl += remaining_quantity * (close_price - entry_price)
                total_same_day_loss_avoided += round(simulated_pnl - baseline_hold_pnl, 4)

            variant_rows.append(
                {
                    "reversal_fraction": reversal_fraction,
                    "same_day_loss_avoided_total": round(total_same_day_loss_avoided, 4),
                    "simulated_order_count": simulated_order_count,
                    "reversal_execution_count": reversal_execution_count,
                    "severe_execution_count": severe_execution_count,
                    "blocked_mild_session_count": blocked_mild_session_count,
                    "blocked_late_severe_count": blocked_late_severe_count,
                }
            )

        best_row = max(variant_rows, key=lambda row: (row["same_day_loss_avoided_total"], -row["simulated_order_count"]))
        current_row = next(row for row in variant_rows if row["reversal_fraction"] == 0.5)

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(variant_rows[0].keys()))
            writer.writeheader()
            writer.writerows(variant_rows)

        summary = {
            "acceptance_posture": "freeze_v134ac_commercial_aerospace_reversal_sell_fraction_audit_v1",
            "current_reversal_fraction": 0.5,
            "best_reversal_fraction": best_row["reversal_fraction"],
            "current_same_day_loss_avoided_total": current_row["same_day_loss_avoided_total"],
            "best_same_day_loss_avoided_total": best_row["same_day_loss_avoided_total"],
            "same_day_loss_avoided_delta": round(
                best_row["same_day_loss_avoided_total"] - current_row["same_day_loss_avoided_total"], 4
            ),
            "variant_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_reversal_sell_fraction_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AC audits the next natural supervision question after the late-severe refinement: how large should the first reversal sell be inside the current wider phase-2 reference.",
            "The surface, clock, severe behavior, mild block, and late-severe block all stay fixed; only the reversal sell fraction changes.",
        ]
        return V134ACCommercialAerospaceReversalSellFractionAuditReport(
            summary=summary,
            variant_rows=variant_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ACCommercialAerospaceReversalSellFractionAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ACCommercialAerospaceReversalSellFractionAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ac_commercial_aerospace_reversal_sell_fraction_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
