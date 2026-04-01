from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
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
class V115FCpoNegativeSampleEnrichmentAndActionLabelExpansionReport:
    summary: dict[str, Any]
    context_count_rows: list[dict[str, Any]]
    enriched_sample_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "context_count_rows": self.context_count_rows,
            "enriched_sample_rows": self.enriched_sample_rows,
            "interpretation": self.interpretation,
        }


class V115FCpoNegativeSampleEnrichmentAndActionLabelExpansionAnalyzer:
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
    def _context_counts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        counts: dict[str, int] = {}
        negative_counts: dict[str, int] = {}
        for row in rows:
            context = str(row["action_context"])
            counts[context] = counts.get(context, 0) + 1
            if _to_bool(row.get("is_negative_enrichment")):
                negative_counts[context] = negative_counts.get(context, 0) + 1
        return [
            {
                "action_context": context,
                "row_count": counts[context],
                "negative_enrichment_row_count": negative_counts.get(context, 0),
            }
            for context in sorted(counts)
        ]

    def analyze(
        self,
        *,
        v114t_payload: dict[str, Any],
        training_rows: list[dict[str, Any]],
    ) -> tuple[V115FCpoNegativeSampleEnrichmentAndActionLabelExpansionReport, list[dict[str, Any]]]:
        summary_t = dict(v114t_payload.get("summary", {}))
        if str(summary_t.get("acceptance_posture")) != "freeze_v114t_cpo_replay_integrity_repair_v1":
            raise ValueError("V115F expects V114T repaired replay.")

        daily_bars = self._load_daily_bars(
            self.repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
        )
        ordered_dates = sorted({dt for _, dt in daily_bars.keys()})
        next_trade_date_map = self._next_trade_date_map(daily_bars)
        positions_by_date = self._reconstruct_positions(list(v114t_payload.get("executed_order_rows", [])))

        existing_keys = {
            (str(row.get("signal_trade_date") or row.get("trade_date")), str(row["symbol"]), str(row["action_context"]))
            for row in training_rows
        }

        enriched_rows = [dict(row) for row in training_rows]
        negative_additions: list[dict[str, Any]] = []

        for replay_day in list(v114t_payload.get("replay_day_rows", [])):
            trade_date = parse_trade_date(str(replay_day["trade_date"]))
            held_symbols = sorted(self._positions_as_of(positions_by_date=positions_by_date, trade_date=trade_date))
            if not held_symbols:
                continue

            avg_return = float(replay_day["board_context"]["avg_return"])
            breadth = float(replay_day["board_context"]["breadth"])
            if not (avg_return <= -0.03 or breadth <= -0.5):
                continue

            execution_date = next_trade_date_map.get(trade_date)
            if execution_date is None:
                continue

            for symbol in held_symbols:
                key = (str(trade_date), symbol, "reduce_vs_hold")
                if key in existing_keys:
                    continue

                execution_bar = daily_bars.get((symbol, execution_date))
                if execution_bar is None:
                    continue

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

                forward_close = labels["forward_close_return"]
                adverse = labels["max_adverse_return"]
                favorable = labels["max_favorable_return"]

                reduce_avoided_drawdown_proxy = round(abs(min(0.0, adverse)), 6)
                reduce_payoff_decay_vs_hold_proxy = round(-forward_close, 6)
                close_invalidation_realized_proxy = round(
                    1.0 if (forward_close <= -0.05 or adverse <= -0.06) else 0.0,
                    6,
                )
                close_opportunity_cost_proxy = round(max(0.0, favorable), 6)

                reduce_favored = bool(forward_close < -0.03 or adverse <= -0.05)
                close_favored = bool(forward_close < -0.06 or adverse <= -0.08)
                action_context = "close_vs_hold" if close_favored else "reduce_vs_hold"

                assembled = {
                    "symbol": symbol,
                    "trade_date": str(trade_date),
                    "signal_trade_date": str(trade_date),
                    "execution_trade_date": str(execution_date),
                    "execution_open_price": round(float(execution_bar["open"]), 6),
                    "action_context": action_context,
                    "held_before_signal": True,
                    "is_repaired_miss_window": False,
                    "is_negative_enrichment": True,
                    "board_phase": "divergence_and_decay" if breadth <= -0.5 else "mixed_risk",
                    "control_label": "holding_veto" if close_favored else "de_risk",
                    "reason": "repaired_replay_negative_sample_enrichment",
                    "role_family": "repaired_negative_window",
                    "board_avg_return": round(avg_return, 6),
                    "board_breadth": round(breadth, 6),
                    "forward_close_return_3d": forward_close,
                    "max_favorable_return_3d": favorable,
                    "max_adverse_return_3d": adverse,
                    "expectancy_proxy_3d": labels["expectancy_proxy"],
                    "action_favored_3d": reduce_favored or close_favored,
                    "P_reduce_avoided_drawdown_proxy_3d": reduce_avoided_drawdown_proxy,
                    "reduce_payoff_decay_vs_hold_proxy_3d": reduce_payoff_decay_vs_hold_proxy,
                    "P_close_invalidation_realized_proxy_3d": close_invalidation_realized_proxy,
                    "P_close_opportunity_cost_proxy_3d": close_opportunity_cost_proxy,
                }
                negative_additions.append(assembled)
                existing_keys.add((str(trade_date), symbol, action_context))

        enriched_rows.extend(negative_additions)
        context_rows = self._context_counts(enriched_rows)

        add_rows = [row for row in enriched_rows if str(row["action_context"]) == "add_vs_hold"]
        reduce_rows = [row for row in enriched_rows if str(row["action_context"]) == "reduce_vs_hold"]
        close_rows = [row for row in enriched_rows if str(row["action_context"]) == "close_vs_hold"]

        summary = {
            "acceptance_posture": "freeze_v115f_cpo_negative_sample_enrichment_and_action_label_expansion_v1",
            "base_training_row_count": len(training_rows),
            "enriched_training_row_count": len(enriched_rows),
            "negative_enrichment_row_count": len(negative_additions),
            "reduce_row_count_after_enrichment": len(reduce_rows),
            "close_row_count_after_enrichment": len(close_rows),
            "add_row_count_after_enrichment": len(add_rows),
            "contains_v114s_style_reduce_close_proxy_labels": len(negative_additions) > 0,
            "recommended_next_posture": "rebuild_intraday_candidate_overlay_on_v115f_balanced_action_table_before_any_promotion",
        }

        interpretation = [
            "V115F thickens the weakest side of the intraday action table: reduce/close contexts.",
            "The goal is not to invent new positive windows, but to stop the Baostock line from being trained almost entirely as an add-biased confirmation layer.",
            "This is still proxy supervision, but it moves the table one step closer to the V114S conditional-expectancy semantics.",
        ]

        report = V115FCpoNegativeSampleEnrichmentAndActionLabelExpansionReport(
            summary=summary,
            context_count_rows=context_rows,
            enriched_sample_rows=negative_additions[:8],
            interpretation=interpretation,
        )
        return report, enriched_rows


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V115FCpoNegativeSampleEnrichmentAndActionLabelExpansionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V115FCpoNegativeSampleEnrichmentAndActionLabelExpansionAnalyzer(repo_root=repo_root)
    with (repo_root / "data" / "training" / "cpo_midfreq_action_outcome_training_rows_v1.csv").open("r", encoding="utf-8") as handle:
        training_rows = list(csv.DictReader(handle))
    result, enriched_rows = analyzer.analyze(
        v114t_payload=load_json_report(repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json"),
        training_rows=training_rows,
    )
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_midfreq_action_outcome_training_rows_enriched_v1.csv",
        rows=enriched_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115f_cpo_negative_sample_enrichment_and_action_label_expansion_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
