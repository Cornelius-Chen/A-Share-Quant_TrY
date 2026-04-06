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
from a_share_quant.strategy.v134l_commercial_aerospace_intraday_broader_hit_simulator_v1 import (
    _round_lot_quantity,
)


@dataclass(slots=True)
class V134AGCommercialAerospaceReversalFullHorizonSanityAuditV1Report:
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


class V134AGCommercialAerospaceReversalFullHorizonSanityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.hit_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_local_1min_session_expansion_hits_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.daily_bars_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.reference_notional = 100000.0
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reversal_full_horizon_sanity_audit_v1.csv"
        )

    def _load_hit_rows(self) -> list[dict[str, Any]]:
        with self.hit_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [row for row in csv.DictReader(handle) if row["predicted_tier"] == "reversal_watch"]

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

    def _load_daily_close_map(self) -> dict[str, list[tuple[str, float]]]:
        close_map: dict[str, list[tuple[str, float]]] = {}
        with self.daily_bars_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                symbol = row["symbol"]
                close_map.setdefault(symbol, []).append((row["trade_date"], float(row["close"])))
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

    def analyze(self) -> V134AGCommercialAerospaceReversalFullHorizonSanityAuditV1Report:
        hit_rows = self._load_hit_rows()
        close_map = self._load_daily_close_map()
        session_rows: list[dict[str, Any]] = []

        for hit_row in hit_rows:
            trade_date = hit_row["trade_date"]
            symbol = hit_row["symbol"]
            full_session_rows = self._load_full_session_rows(trade_date, symbol)
            if not full_session_rows:
                continue
            entry_price = float(full_session_rows[0]["open_px"])
            quantity = _round_lot_quantity(entry_price, self.reference_notional)
            if quantity <= 0:
                continue
            onsets = self._detect_state_onsets(full_session_rows)
            reversal_minute = onsets["reversal_watch"]
            if reversal_minute is None:
                continue
            fill_minute = reversal_minute + 1
            if fill_minute > len(full_session_rows):
                continue
            fill_price = float(full_session_rows[fill_minute - 1]["open_px"])
            symbol_closes = close_map.get(symbol, [])
            future_1d = self._future_close(symbol_closes, trade_date, 1)
            future_3d = self._future_close(symbol_closes, trade_date, 3)
            future_5d = self._future_close(symbol_closes, trade_date, 5)

            row = {
                "trade_date": trade_date,
                "symbol": symbol,
                "month_bucket": hit_row["month_bucket"],
                "reversal_minute": reversal_minute,
                "fill_minute": fill_minute,
                "fill_price": round(fill_price, 4),
                "reference_quantity": quantity,
                "horizon_pnl_1d": round(quantity * (future_1d - fill_price), 4) if future_1d is not None else "",
                "horizon_pnl_3d": round(quantity * (future_3d - fill_price), 4) if future_3d is not None else "",
                "horizon_pnl_5d": round(quantity * (future_5d - fill_price), 4) if future_5d is not None else "",
            }
            session_rows.append(row)

        horizon_rows: list[dict[str, Any]] = []
        for horizon in (1, 3, 5):
            key = f"horizon_pnl_{horizon}d"
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

        best_horizon_row = next(row for row in horizon_rows if row["horizon_days"] == 5)
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        summary = {
            "acceptance_posture": "freeze_v134ag_commercial_aerospace_reversal_full_horizon_sanity_audit_v1",
            "reversal_session_count": len(session_rows),
            "net_horizon_pnl_if_held_1d": next(row for row in horizon_rows if row["horizon_days"] == 1)["net_horizon_pnl_if_held"],
            "net_horizon_pnl_if_held_3d": next(row for row in horizon_rows if row["horizon_days"] == 3)["net_horizon_pnl_if_held"],
            "net_horizon_pnl_if_held_5d": best_horizon_row["net_horizon_pnl_if_held"],
            "session_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_reversal_full_horizon_sanity_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AG checks the cost of promoting full reversal exit under horizons longer than same-day.",
            "It does not reopen replay or change the surface; it only asks whether the stronger same-day defensive result is later offset by rebound opportunity cost.",
        ]
        return V134AGCommercialAerospaceReversalFullHorizonSanityAuditV1Report(
            summary=summary,
            horizon_rows=horizon_rows,
            session_rows=session_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AGCommercialAerospaceReversalFullHorizonSanityAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AGCommercialAerospaceReversalFullHorizonSanityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ag_commercial_aerospace_reversal_full_horizon_sanity_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
