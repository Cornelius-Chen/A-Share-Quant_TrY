from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from statistics import median
from typing import Any, Callable

from a_share_quant.strategy.v115b_cpo_midfreq_intraday_factor_extraction_v1 import (
    _default_fetch_window_rows,
    _window_features,
)
from a_share_quant.strategy.v115c_cpo_midfreq_intraday_miss_window_audit_v1 import _score_row


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


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _to_float(value: Any, default: float = 0.0) -> float:
    text = str(value).strip()
    if text == "":
        return default
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n", ""}:
        return False
    return bool(value)


@dataclass(slots=True)
class V115ECpoBroaderRepairedIntradayThresholdCalibrationReport:
    summary: dict[str, Any]
    threshold_rows: list[dict[str, Any]]
    context_rows: list[dict[str, Any]]
    sample_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_rows": self.threshold_rows,
            "context_rows": self.context_rows,
            "sample_rows": self.sample_rows,
            "interpretation": self.interpretation,
        }


class V115ECpoBroaderRepairedIntradayThresholdCalibrationAnalyzer:
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
        latest = max(eligible)
        return set(positions_by_date[latest])

    @staticmethod
    def _next_trade_date_map(daily_bars: dict[tuple[str, date], dict[str, float]]) -> dict[date, date]:
        ordered_dates = sorted({dt for _, dt in daily_bars.keys()})
        return {ordered_dates[idx]: ordered_dates[idx + 1] for idx in range(len(ordered_dates) - 1)}

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
        selected_dates = ordered_dates[date_index[execution_date]:date_index[execution_date] + horizon]
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
    def _context_from_replay_day(row: dict[str, Any]) -> str | None:
        avg_return = float(row["board_context"]["avg_return"])
        breadth = float(row["board_context"]["breadth"])
        exposure = float(row["gross_exposure_after_close"])
        actions = int(row["executed_today_order_count"])

        if avg_return >= 0.05 and breadth >= 0.8:
            return "strong_under_exposed" if exposure < 0.22 else "strong_supported"
        if avg_return <= -0.03 and breadth <= -0.5 and exposure >= 0.10:
            return "risk_pressure"
        if actions > 0 and exposure > 0.0:
            return "action_mixed"
        return None

    @staticmethod
    def _calibrate_threshold(score_rows: list[dict[str, Any]], *, score_key: str) -> dict[str, float]:
        labeled_rows = [
            row for row in score_rows
            if bool(row.get("add_favored_3d")) or bool(row.get("risk_favored_3d"))
        ]
        if not labeled_rows:
            return {
                "best_threshold": 0.5,
                "balanced_accuracy": 0.0,
                "positive_pass_rate": 0.0,
                "negative_fail_rate": 0.0,
            }

        grid = [round(0.30 + step * 0.01, 2) for step in range(31)]
        best: dict[str, float] | None = None
        for threshold in grid:
            positives = [row for row in labeled_rows if bool(row.get("add_favored_3d"))]
            negatives = [row for row in labeled_rows if bool(row.get("risk_favored_3d"))]
            positive_pass = sum(1 for row in positives if _to_float(row.get(score_key, 0.0)) >= threshold)
            negative_fail = sum(1 for row in negatives if _to_float(row.get(score_key, 0.0)) < threshold)
            positive_pass_rate = positive_pass / max(len(positives), 1)
            negative_fail_rate = negative_fail / max(len(negatives), 1)
            balanced_accuracy = 0.5 * (positive_pass_rate + negative_fail_rate)
            candidate = {
                "best_threshold": round(threshold, 6),
                "balanced_accuracy": round(balanced_accuracy, 6),
                "positive_pass_rate": round(positive_pass_rate, 6),
                "negative_fail_rate": round(negative_fail_rate, 6),
            }
            if best is None:
                best = candidate
                continue
            if (
                candidate["balanced_accuracy"] > best["balanced_accuracy"]
                or (
                    candidate["balanced_accuracy"] == best["balanced_accuracy"]
                    and candidate["best_threshold"] > best["best_threshold"]
                )
            ):
                best = candidate
        return best or {
            "best_threshold": 0.5,
            "balanced_accuracy": 0.0,
            "positive_pass_rate": 0.0,
            "negative_fail_rate": 0.0,
        }

    def analyze_from_training_rows(
        self,
        *,
        training_rows: list[dict[str, Any]],
    ) -> tuple[V115ECpoBroaderRepairedIntradayThresholdCalibrationReport, list[dict[str, Any]]]:
        usable_rows = [
            dict(row) for row in training_rows
            if str(row.get("fetch_status", "success")) == "success"
            and str(row.get("action_context")) in {"add_vs_hold", "entry_vs_skip", "reduce_vs_hold", "close_vs_hold"}
        ]
        for row in usable_rows:
            row["context_label"] = str(row.get("action_context"))
            row["is_top_miss_day"] = _to_bool(row.get("is_repaired_miss_window"))
            row["add_favored_3d"] = _to_bool(row.get("action_favored_3d")) if str(row.get("action_context")) in {"add_vs_hold", "entry_vs_skip"} else False
            row["risk_favored_3d"] = _to_bool(row.get("action_favored_3d")) if str(row.get("action_context")) in {"reduce_vs_hold", "close_vs_hold"} else False

        threshold_rows: list[dict[str, Any]] = []
        thresholds: dict[str, float] = {}
        for frequency in ("30", "60"):
            score_key = f"f{frequency}_confirmation_score"
            metrics = self._calibrate_threshold(usable_rows, score_key=score_key)
            thresholds[score_key] = metrics["best_threshold"]
            threshold_rows.append(
                {
                    "frequency": frequency,
                    **metrics,
                    "positive_reference_count": sum(1 for row in usable_rows if bool(row.get("add_favored_3d"))),
                    "negative_reference_count": sum(1 for row in usable_rows if bool(row.get("risk_favored_3d"))),
                }
            )

        for row in usable_rows:
            row["f30_threshold_pass"] = bool(_to_float(row.get("f30_confirmation_score", 0.0)) >= float(thresholds["f30_confirmation_score"]))
            row["f60_threshold_pass"] = bool(_to_float(row.get("f60_confirmation_score", 0.0)) >= float(thresholds["f60_confirmation_score"]))

        context_names = sorted({str(row["context_label"]) for row in usable_rows})
        context_rows: list[dict[str, Any]] = []
        for context_name in context_names:
            rows = [row for row in usable_rows if str(row["context_label"]) == context_name]
            context_rows.append(
                {
                    "context_label": context_name,
                    "row_count": len(rows),
                    "top_miss_row_count": sum(1 for row in rows if bool(row["is_top_miss_day"])),
                    "add_favored_rate_3d": round(_mean([1.0 if bool(row["add_favored_3d"]) else 0.0 for row in rows]), 6),
                    "risk_favored_rate_3d": round(_mean([1.0 if bool(row["risk_favored_3d"]) else 0.0 for row in rows]), 6),
                    "f30_pass_rate": round(_mean([1.0 if bool(row.get("f30_threshold_pass")) else 0.0 for row in rows]), 6),
                    "f60_pass_rate": round(_mean([1.0 if bool(row.get("f60_threshold_pass")) else 0.0 for row in rows]), 6),
                    "median_expectancy_proxy_3d": round(median(_to_float(row["expectancy_proxy_3d"]) for row in rows), 6),
                }
            )

        miss_rows = [row for row in usable_rows if bool(row.get("is_top_miss_day"))]
        candidate_miss_rows = [
            row for row in miss_rows if bool(row.get("f30_threshold_pass")) or bool(row.get("f60_threshold_pass"))
        ]

        summary = {
            "acceptance_posture": "freeze_v115e_cpo_broader_repaired_intraday_threshold_calibration_v1",
            "selected_replay_day_count": len({str(row.get("signal_trade_date") or row.get("trade_date")) for row in usable_rows}),
            "calibration_row_count": len(usable_rows),
            "successful_row_count": len(usable_rows),
            "top_miss_row_count": len(miss_rows),
            "strong_under_exposed_row_count": sum(1 for row in usable_rows if str(row.get("action_context")) == "add_vs_hold"),
            "candidate_miss_row_count": len(candidate_miss_rows),
            "f30_best_threshold": thresholds.get("f30_confirmation_score", 0.0),
            "f60_best_threshold": thresholds.get("f60_confirmation_score", 0.0),
            "candidate_only_posture_retained": True,
            "recommended_next_posture": "use_v115e_recalibrated_thresholds_as_harder_candidate_overlay_and_expand_action_outcome_labels_before_any_promotion",
        }

        interpretation = [
            "V115E recalibrates the mid-frequency 30/60min confirmation thresholds on the broader repaired action-timepoint table from V115D rather than only the narrow V115C miss-day slice.",
            "This is intentionally harder than the first permissive miss-window threshold because it must survive entry/add and reduce/close contexts together on the repaired replay base.",
            "The output is still candidate-only, but it is materially closer to lawful intraday action learning than the original 10/10 miss-window confirmation pass.",
        ]

        report = V115ECpoBroaderRepairedIntradayThresholdCalibrationReport(
            summary=summary,
            threshold_rows=threshold_rows,
            context_rows=context_rows,
            sample_rows=usable_rows[:10],
            interpretation=interpretation,
        )
        return report, usable_rows

    def analyze(
        self,
        *,
        v114t_payload: dict[str, Any],
        v114w_payload: dict[str, Any],
        fetch_window_rows: Callable[[str, str, str], list[dict[str, Any]]] = _default_fetch_window_rows,
        frequencies: tuple[str, ...] = ("30", "60"),
    ) -> tuple[V115ECpoBroaderRepairedIntradayThresholdCalibrationReport, list[dict[str, Any]]]:
        summary_t = dict(v114t_payload.get("summary", {}))
        summary_w = dict(v114w_payload.get("summary", {}))
        if str(summary_t.get("acceptance_posture")) != "freeze_v114t_cpo_replay_integrity_repair_v1":
            raise ValueError("V115E expects V114T repaired replay.")
        if str(summary_w.get("acceptance_posture")) != "freeze_v114w_cpo_under_exposure_attribution_repaired_v1":
            raise ValueError("V115E expects V114W repaired under-exposure attribution.")

        daily_bars = self._load_daily_bars(
            self.repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
        )
        ordered_dates = sorted({dt for _, dt in daily_bars.keys()})
        next_trade_date_map = self._next_trade_date_map(daily_bars)
        positions_by_date = self._reconstruct_positions(list(v114t_payload.get("executed_order_rows", [])))
        top_miss_dates = {str(row["trade_date"]) for row in list(v114w_payload.get("top_opportunity_miss_rows", []))}

        selected_days: list[dict[str, Any]] = []
        for replay_day in list(v114t_payload.get("replay_day_rows", [])):
            trade_date = parse_trade_date(str(replay_day["trade_date"]))
            held_symbols = sorted(self._positions_as_of(positions_by_date=positions_by_date, trade_date=trade_date))
            if not held_symbols:
                continue
            context_label = self._context_from_replay_day(replay_day)
            if context_label is None:
                continue
            selected_days.append(
                {
                    "trade_date": str(trade_date),
                    "context_label": context_label,
                    "is_top_miss_day": str(trade_date) in top_miss_dates,
                    "held_symbols": held_symbols,
                    "board_avg_return": float(replay_day["board_context"]["avg_return"]),
                    "board_breadth": float(replay_day["board_context"]["breadth"]),
                    "gross_exposure_after_close": float(replay_day["gross_exposure_after_close"]),
                    "executed_today_order_count": int(replay_day["executed_today_order_count"]),
                }
            )

        calibration_rows: list[dict[str, Any]] = []
        for day_row in selected_days:
            signal_date = parse_trade_date(str(day_row["trade_date"]))
            execution_date = next_trade_date_map.get(signal_date)
            if execution_date is None:
                continue
            for symbol in list(day_row["held_symbols"]):
                execution_bar = daily_bars.get((symbol, execution_date))
                if execution_bar is None:
                    continue
                assembled: dict[str, Any] = {
                    "trade_date": str(signal_date),
                    "execution_trade_date": str(execution_date),
                    "symbol": symbol,
                    "context_label": str(day_row["context_label"]),
                    "is_top_miss_day": bool(day_row["is_top_miss_day"]),
                    "board_avg_return": float(day_row["board_avg_return"]),
                    "board_breadth": float(day_row["board_breadth"]),
                    "gross_exposure_after_close": float(day_row["gross_exposure_after_close"]),
                    "executed_today_order_count": int(day_row["executed_today_order_count"]),
                    "execution_open_price": round(float(execution_bar["open"]), 6),
                }
                try:
                    for frequency in frequencies:
                        rows = fetch_window_rows(symbol, str(signal_date), frequency)
                        assembled.update(_window_features(rows, frequency=frequency))
                        prefix = f"f{frequency}_"
                        assembled[f"{prefix}confirmation_score"] = _score_row(assembled, prefix=prefix)
                except Exception as exc:  # pragma: no cover - live run path
                    assembled["fetch_status"] = "error"
                    assembled["error_type"] = type(exc).__name__
                    assembled["error_message"] = str(exc)
                    calibration_rows.append(assembled)
                    continue

                assembled["fetch_status"] = "success"
                future_rows = self._future_path(
                    symbol=symbol,
                    execution_date=execution_date,
                    daily_bars=daily_bars,
                    ordered_dates=ordered_dates,
                    horizon=3,
                )
                labels = self._compute_horizon_labels(
                    execution_open=float(execution_bar["open"]),
                    future_rows=future_rows,
                )
                assembled["forward_close_return_3d"] = labels["forward_close_return"]
                assembled["max_favorable_return_3d"] = labels["max_favorable_return"]
                assembled["max_adverse_return_3d"] = labels["max_adverse_return"]
                assembled["expectancy_proxy_3d"] = labels["expectancy_proxy"]
                assembled["add_favored_3d"] = bool(
                    float(assembled["forward_close_return_3d"]) > 0.03
                    and float(assembled["max_adverse_return_3d"]) > -0.04
                )
                assembled["risk_favored_3d"] = bool(
                    float(assembled["forward_close_return_3d"]) < -0.03
                    or float(assembled["max_adverse_return_3d"]) <= -0.05
                )
                calibration_rows.append(assembled)

        successful_rows = [row for row in calibration_rows if row.get("fetch_status") == "success"]
        threshold_rows: list[dict[str, Any]] = []
        thresholds: dict[str, float] = {}
        for frequency in frequencies:
            score_key = f"f{frequency}_confirmation_score"
            metrics = self._calibrate_threshold(successful_rows, score_key=score_key)
            thresholds[score_key] = metrics["best_threshold"]
            threshold_rows.append(
                {
                    "frequency": frequency,
                    **metrics,
                    "positive_reference_count": sum(1 for row in successful_rows if bool(row.get("add_favored_3d"))),
                    "negative_reference_count": sum(1 for row in successful_rows if bool(row.get("risk_favored_3d"))),
                }
            )

        for row in successful_rows:
            for frequency in frequencies:
                score_key = f"f{frequency}_confirmation_score"
                pass_key = f"f{frequency}_threshold_pass"
                row[pass_key] = bool(float(row.get(score_key, 0.0)) >= float(thresholds[score_key]))

        context_names = sorted({str(row["context_label"]) for row in successful_rows})
        context_rows: list[dict[str, Any]] = []
        for context_name in context_names:
            rows = [row for row in successful_rows if str(row["context_label"]) == context_name]
            context_rows.append(
                {
                    "context_label": context_name,
                    "row_count": len(rows),
                    "top_miss_row_count": sum(1 for row in rows if bool(row["is_top_miss_day"])),
                    "add_favored_rate_3d": round(_mean([1.0 if bool(row["add_favored_3d"]) else 0.0 for row in rows]), 6),
                    "risk_favored_rate_3d": round(_mean([1.0 if bool(row["risk_favored_3d"]) else 0.0 for row in rows]), 6),
                    "f30_pass_rate": round(_mean([1.0 if bool(row.get("f30_threshold_pass")) else 0.0 for row in rows]), 6),
                    "f60_pass_rate": round(_mean([1.0 if bool(row.get("f60_threshold_pass")) else 0.0 for row in rows]), 6),
                    "median_expectancy_proxy_3d": round(median(float(row["expectancy_proxy_3d"]) for row in rows), 6),
                }
            )

        miss_rows = [row for row in successful_rows if str(row["context_label"]) == "strong_under_exposed"]
        candidate_miss_rows = [
            row for row in miss_rows if bool(row.get("f30_threshold_pass")) or bool(row.get("f60_threshold_pass"))
        ]

        summary = {
            "acceptance_posture": "freeze_v115e_cpo_broader_repaired_intraday_threshold_calibration_v1",
            "selected_replay_day_count": len(selected_days),
            "calibration_row_count": len(calibration_rows),
            "successful_row_count": len(successful_rows),
            "top_miss_row_count": sum(1 for row in successful_rows if bool(row["is_top_miss_day"])),
            "strong_under_exposed_row_count": len(miss_rows),
            "candidate_miss_row_count": len(candidate_miss_rows),
            "f30_best_threshold": thresholds.get("f30_confirmation_score", 0.0),
            "f60_best_threshold": thresholds.get("f60_confirmation_score", 0.0),
            "candidate_only_posture_retained": True,
            "recommended_next_posture": "use_v115e_recalibrated_thresholds_as_harder_candidate_overlay_and_expand_action_outcome_labels_before_any_promotion",
        }

        interpretation = [
            "V115E expands the repaired intraday calibration universe beyond the six top miss days.",
            "The point is to harden the Baostock 30/60min confirmation thresholds against a broader repaired replay surface that includes strong-supported days and risk-pressure days.",
            "This remains candidate-only: the goal is a harder threshold, not premature intraday law.",
        ]

        report = V115ECpoBroaderRepairedIntradayThresholdCalibrationReport(
            summary=summary,
            threshold_rows=threshold_rows,
            context_rows=context_rows,
            sample_rows=successful_rows[:10],
            interpretation=interpretation,
        )
        return report, calibration_rows


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V115ECpoBroaderRepairedIntradayThresholdCalibrationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V115ECpoBroaderRepairedIntradayThresholdCalibrationAnalyzer(repo_root=repo_root)
    training_rows_path = repo_root / "data" / "training" / "cpo_midfreq_action_outcome_training_rows_v1.csv"
    if training_rows_path.exists():
        with training_rows_path.open("r", encoding="utf-8") as handle:
            training_rows = list(csv.DictReader(handle))
        result, calibration_rows = analyzer.analyze_from_training_rows(training_rows=training_rows)
    else:
        result, calibration_rows = analyzer.analyze(
            v114t_payload=load_json_report(repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json"),
            v114w_payload=load_json_report(repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json"),
        )
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_midfreq_threshold_calibration_rows_v1.csv",
        rows=calibration_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115e_cpo_broader_repaired_intraday_threshold_calibration_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
