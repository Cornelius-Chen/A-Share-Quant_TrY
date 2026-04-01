from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from statistics import median
from typing import Any


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def parse_trade_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def write_csv_rows(*, path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


@dataclass(slots=True)
class V115DCpoMidfreqActionOutcomeTrainingTableReport:
    summary: dict[str, Any]
    context_count_rows: list[dict[str, Any]]
    label_threshold_rows: list[dict[str, Any]]
    sample_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "context_count_rows": self.context_count_rows,
            "label_threshold_rows": self.label_threshold_rows,
            "sample_rows": self.sample_rows,
            "interpretation": self.interpretation,
        }


class V115DCpoMidfreqActionOutcomeTrainingTableAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _load_daily_bars(self, path: Path) -> dict[tuple[str, date], dict[str, float]]:
        rows: dict[tuple[str, date], dict[str, float]] = {}
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                symbol = str(row["symbol"])
                trade_date = parse_trade_date(str(row["trade_date"]))
                rows[(symbol, trade_date)] = {
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                }
        return rows

    @staticmethod
    def _reconstruct_positions(executed_rows: list[dict[str, Any]]) -> dict[date, set[str]]:
        positions: dict[str, int] = {}
        by_date: dict[date, list[dict[str, Any]]] = {}
        for row in executed_rows:
            exec_date = parse_trade_date(str(row["execution_trade_date"]))
            by_date.setdefault(exec_date, []).append(row)

        positions_by_date: dict[date, set[str]] = {}
        for exec_date in sorted(by_date):
            for row in by_date[exec_date]:
                symbol = str(row["symbol"])
                quantity = int(row["quantity"])
                if str(row["action"]) == "buy":
                    positions[symbol] = positions.get(symbol, 0) + quantity
                else:
                    positions[symbol] = max(0, positions.get(symbol, 0) - quantity)
            positions_by_date[exec_date] = {symbol for symbol, quantity in positions.items() if quantity > 0}
        return positions_by_date

    @staticmethod
    def _positions_as_of(*, positions_by_date: dict[date, set[str]], trade_date: date) -> set[str]:
        eligible = [dt for dt in positions_by_date if dt <= trade_date]
        if not eligible:
            return set()
        latest_date = max(eligible)
        return set(positions_by_date[latest_date])

    @staticmethod
    def _next_trade_date_map(daily_bars: dict[tuple[str, date], dict[str, float]]) -> dict[date, date]:
        ordered = sorted({dt for _, dt in daily_bars.keys()})
        return {ordered[idx]: ordered[idx + 1] for idx in range(len(ordered) - 1)}

    @staticmethod
    def _future_path(
        *,
        symbol: str,
        execution_date: date,
        daily_bars: dict[tuple[str, date], dict[str, float]],
        ordered_dates: list[date],
        horizon: int,
    ) -> list[dict[str, float]]:
        date_index = {dt: idx for idx, dt in enumerate(ordered_dates)}
        if execution_date not in date_index:
            return []
        start_idx = date_index[execution_date]
        selected_dates = ordered_dates[start_idx:start_idx + horizon]
        rows: list[dict[str, float]] = []
        for dt in selected_dates:
            payload = daily_bars.get((symbol, dt))
            if payload is not None:
                rows.append(payload)
        return rows

    @staticmethod
    def _compute_horizon_labels(*, execution_open: float, future_rows: list[dict[str, float]]) -> dict[str, float]:
        if execution_open <= 0 or not future_rows:
            return {
                "forward_close_return": 0.0,
                "max_favorable_return": 0.0,
                "max_adverse_return": 0.0,
                "expectancy_proxy": 0.0,
            }
        close_return = float(future_rows[-1]["close"]) / execution_open - 1.0
        favorable = max(float(row["high"]) / execution_open - 1.0 for row in future_rows)
        adverse = min(float(row["low"]) / execution_open - 1.0 for row in future_rows)
        expectancy_proxy = close_return + 0.5 * favorable - abs(min(0.0, adverse))
        return {
            "forward_close_return": round(close_return, 6),
            "max_favorable_return": round(favorable, 6),
            "max_adverse_return": round(adverse, 6),
            "expectancy_proxy": round(expectancy_proxy, 6),
        }

    @staticmethod
    def _action_context(*, control_label: str, held_before_signal: bool) -> str:
        if control_label == "eligibility":
            return "add_vs_hold" if held_before_signal else "entry_vs_skip"
        if control_label == "de_risk":
            return "reduce_vs_hold"
        if control_label == "holding_veto":
            return "close_vs_hold"
        return "other"

    def analyze(
        self,
        *,
        v114t_payload: dict[str, Any],
        v115b_payload: dict[str, Any],
        v115c_payload: dict[str, Any],
    ) -> tuple[V115DCpoMidfreqActionOutcomeTrainingTableReport, list[dict[str, Any]]]:
        summary_t = dict(v114t_payload.get("summary", {}))
        summary_b = dict(v115b_payload.get("summary", {}))
        summary_c = dict(v115c_payload.get("summary", {}))
        if str(summary_t.get("acceptance_posture")) != "freeze_v114t_cpo_replay_integrity_repair_v1":
            raise ValueError("V115D expects V114T repaired replay.")
        if str(summary_b.get("acceptance_posture")) != "freeze_v115b_cpo_midfreq_intraday_factor_extraction_v1":
            raise ValueError("V115D expects V115B mid-frequency factor extraction.")
        if str(summary_c.get("acceptance_posture")) != "freeze_v115c_cpo_midfreq_intraday_miss_window_audit_v1":
            raise ValueError("V115D expects V115C miss-window audit.")

        factor_rows = [row for row in list(v115b_payload.get("factor_rows", [])) if row.get("fetch_status") == "success"]
        miss_rows = [row for row in list(v115c_payload.get("miss_window_rows", [])) if row.get("fetch_status", "success") == "success"]
        miss_keys = {
            (str(row["trade_date"]), str(row["symbol"]))
            for row in miss_rows
        }
        existing_keys = {(str(row["trade_date"]), str(row["symbol"])) for row in factor_rows}
        supplemental_rows = []
        for row in miss_rows:
            key = (str(row["trade_date"]), str(row["symbol"]))
            if key in existing_keys:
                continue
            supplemental_rows.append(
                {
                    **row,
                    "fetch_status": "success",
                    "control_label": "eligibility",
                    "board_phase": "main_markup",
                    "reason": "repaired_miss_day_add_candidate",
                    "role_family": "repaired_miss_window",
                    "forced_action_context": "add_vs_hold",
                }
            )
        source_rows = factor_rows + supplemental_rows

        executed_rows = list(v114t_payload.get("executed_order_rows", []))
        positions_by_date = self._reconstruct_positions(executed_rows)

        daily_bars = self._load_daily_bars(
            self.repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
        )
        next_trade_date_map = self._next_trade_date_map(daily_bars)
        ordered_dates = sorted({dt for _, dt in daily_bars.keys()})

        training_rows: list[dict[str, Any]] = []
        for row in source_rows:
            signal_date = parse_trade_date(str(row["trade_date"]))
            symbol = str(row["symbol"])
            execution_date = next_trade_date_map.get(signal_date)
            if execution_date is None:
                continue
            execution_bar = daily_bars.get((symbol, execution_date))
            if execution_bar is None:
                continue
            held_before_signal = symbol in self._positions_as_of(positions_by_date=positions_by_date, trade_date=signal_date)
            action_context = str(row.get("forced_action_context", "")) or self._action_context(
                control_label=str(row["control_label"]),
                held_before_signal=held_before_signal,
            )
            if action_context == "other":
                continue

            assembled = dict(row)
            assembled["signal_trade_date"] = str(signal_date)
            assembled["execution_trade_date"] = str(execution_date)
            assembled["execution_open_price"] = round(float(execution_bar["open"]), 6)
            assembled["held_before_signal"] = held_before_signal
            assembled["action_context"] = action_context
            assembled["is_repaired_miss_window"] = (str(signal_date), symbol) in miss_keys

            for horizon in (1, 3, 5):
                future_rows = self._future_path(
                    symbol=symbol,
                    execution_date=execution_date,
                    daily_bars=daily_bars,
                    ordered_dates=ordered_dates,
                    horizon=horizon,
                )
                labels = self._compute_horizon_labels(
                    execution_open=float(execution_bar["open"]),
                    future_rows=future_rows,
                )
                assembled[f"forward_close_return_{horizon}d"] = labels["forward_close_return"]
                assembled[f"max_favorable_return_{horizon}d"] = labels["max_favorable_return"]
                assembled[f"max_adverse_return_{horizon}d"] = labels["max_adverse_return"]
                assembled[f"expectancy_proxy_{horizon}d"] = labels["expectancy_proxy"]

            fwd3 = float(assembled["forward_close_return_3d"])
            mae3 = float(assembled["max_adverse_return_3d"])
            if action_context in {"add_vs_hold", "entry_vs_skip"}:
                assembled["action_favored_3d"] = bool(fwd3 > 0.03 and mae3 > -0.04)
            else:
                assembled["action_favored_3d"] = bool(fwd3 < -0.03 or mae3 <= -0.05)

            training_rows.append(assembled)

        context_counts: dict[str, int] = {}
        miss_context_counts: dict[str, int] = {}
        for row in training_rows:
            context = str(row["action_context"])
            context_counts[context] = context_counts.get(context, 0) + 1
            if bool(row["is_repaired_miss_window"]):
                miss_context_counts[context] = miss_context_counts.get(context, 0) + 1

        context_count_rows = [
            {
                "action_context": key,
                "row_count": value,
                "miss_window_row_count": miss_context_counts.get(key, 0),
            }
            for key, value in sorted(context_counts.items())
        ]

        label_threshold_rows = []
        for context in sorted(context_counts):
            context_rows = [row for row in training_rows if str(row["action_context"]) == context]
            label_threshold_rows.append(
                {
                    "action_context": context,
                    "row_count": len(context_rows),
                    "favored_3d_rate": round(
                        sum(1 for row in context_rows if bool(row["action_favored_3d"])) / max(len(context_rows), 1),
                        6,
                    ),
                    "median_expectancy_proxy_3d": round(
                        median(float(row["expectancy_proxy_3d"]) for row in context_rows),
                        6,
                    ),
                    "median_forward_close_return_3d": round(
                        median(float(row["forward_close_return_3d"]) for row in context_rows),
                        6,
                    ),
                    "median_max_adverse_return_3d": round(
                        median(float(row["max_adverse_return_3d"]) for row in context_rows),
                        6,
                    ),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v115d_cpo_midfreq_action_outcome_training_table_v1",
            "training_row_count": len(training_rows),
            "action_context_count": len(context_count_rows),
            "repaired_miss_window_row_count": sum(1 for row in training_rows if bool(row["is_repaired_miss_window"])),
            "contains_add_vs_hold_rows": any(str(row["action_context"]) == "add_vs_hold" for row in training_rows),
            "contains_reduce_close_rows": any(str(row["action_context"]) in {"reduce_vs_hold", "close_vs_hold"} for row in training_rows),
            "midfreq_training_table_ready_for_candidate_supervised_use": len(training_rows) >= 15,
            "recommended_next_posture": "use_v115d_as_candidate_action_outcome_training_table_and_rebuild_thresholds_on_broader_repaired_windows",
        }
        interpretation = [
            "V115D is the first table that aligns Baostock mid-frequency factors with repaired replay timing and action contexts.",
            "The key shift is from static window separation to action-outcome supervision: entry/add/reduce/close are now framed against future path labels on a T+1-open execution base.",
            "This table is still candidate-only, but it is the right substrate for harder intraday thresholds and later add/reduce-vs-hold learning.",
        ]

        sample_rows = training_rows[:8]
        report = V115DCpoMidfreqActionOutcomeTrainingTableReport(
            summary=summary,
            context_count_rows=context_count_rows,
            label_threshold_rows=label_threshold_rows,
            sample_rows=sample_rows,
            interpretation=interpretation,
        )
        return report, training_rows


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V115DCpoMidfreqActionOutcomeTrainingTableReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V115DCpoMidfreqActionOutcomeTrainingTableAnalyzer(repo_root=repo_root)
    result, training_rows = analyzer.analyze(
        v114t_payload=load_json_report(repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json"),
        v115b_payload=load_json_report(repo_root / "reports" / "analysis" / "v115b_cpo_midfreq_intraday_factor_extraction_v1.json"),
        v115c_payload=load_json_report(repo_root / "reports" / "analysis" / "v115c_cpo_midfreq_intraday_miss_window_audit_v1.json"),
    )
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_midfreq_action_outcome_training_rows_v1.csv",
        rows=training_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115d_cpo_midfreq_action_outcome_training_table_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
