from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from a_share_quant.backtest.metrics import mainline_window_breakdown
from a_share_quant.common.config import merge_config
from a_share_quant.common.models import (
    AttackPermission,
    DailyBar,
    Fill,
    HierarchyAssignment,
    MainlineWindow,
    Signal,
)
from a_share_quant.strategy.dataset_comparison import DatasetPack
from a_share_quant.strategy.experiment_runner import StrategyExperimentRunner
from a_share_quant.strategy.rule_sweep import RuleCandidate


@dataclass(frozen=True, slots=True)
class ReplayTargetWindow:
    window_id: str
    symbol: str
    start_date: date
    end_date: date
    capturable_return: float = 0.0


@dataclass(slots=True)
class WindowReplayDiagnosticResult:
    summary: dict[str, Any]
    window_records: list[dict[str, Any]]
    comparison_records: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "window_records": self.window_records,
            "comparison_records": self.comparison_records,
        }


class WindowReplayDiagnostic:
    """Replay a few target windows and explain candidate behavior day by day."""

    def analyze(
        self,
        *,
        dataset_pack: DatasetPack,
        strategy_names: list[str],
        candidates: list[RuleCandidate],
        target_windows: list[ReplayTargetWindow],
        lookback_days: int,
        incumbent_name: str,
        challenger_name: str,
        engine,
    ) -> WindowReplayDiagnosticResult:
        window_records: list[dict[str, Any]] = []
        for candidate in candidates:
            merged_config = merge_config(dataset_pack.config, candidate.override)
            runner = StrategyExperimentRunner.from_config(engine=engine, config=merged_config)
            for strategy_name in strategy_names:
                window_records.extend(
                    self._analyze_candidate_strategy(
                        dataset_pack=dataset_pack,
                        runner=runner,
                        candidate=candidate,
                        strategy_name=strategy_name,
                        target_windows=target_windows,
                        lookback_days=lookback_days,
                    )
                )

        comparison_records = self._build_comparisons(
            window_records=window_records,
            incumbent_name=incumbent_name,
            challenger_name=challenger_name,
        )
        summary = {
            "dataset_name": dataset_pack.dataset_name,
            "strategy_count": len(strategy_names),
            "candidate_count": len(candidates),
            "target_window_count": len(target_windows),
            "comparison_count": len(comparison_records),
            "incumbent_name": incumbent_name,
            "challenger_name": challenger_name,
            "issue_summary": self._issue_summary(comparison_records),
        }
        return WindowReplayDiagnosticResult(
            summary=summary,
            window_records=window_records,
            comparison_records=comparison_records,
        )

    def _analyze_candidate_strategy(
        self,
        *,
        dataset_pack: DatasetPack,
        runner: StrategyExperimentRunner,
        candidate: RuleCandidate,
        strategy_name: str,
        target_windows: list[ReplayTargetWindow],
        lookback_days: int,
    ) -> list[dict[str, Any]]:
        strategy = runner._strategy_from_name(strategy_name)
        bars_by_symbol = runner._bars_by_symbol(dataset_pack.bars)
        sector_scores = runner.scorer.score(dataset_pack.sector_snapshots)
        segments = runner._build_segments(sector_scores=sector_scores, index_bars=dataset_pack.index_bars or [])
        permissions = runner.permission_engine.evaluate(sector_scores, segments)
        allowed_sector_ids = {
            permission.approved_sector_id
            for permission in permissions
            if permission.is_attack_allowed and permission.approved_sector_id is not None
        }
        assignments = runner.hierarchy_ranker.rank(
            dataset_pack.stock_snapshots,
            allowed_sector_ids=allowed_sector_ids or None,
        )
        assignment_lookup = {
            (assignment.trade_date, assignment.symbol): assignment
            for assignment in assignments
        }
        current_positions: dict[str, int] = {}
        pending_signals_by_fill_date: dict[date, list[Signal]] = {}
        pending_buy_symbols: set[str] = set()
        pending_sell_symbols: set[str] = set()
        signals: list[Signal] = []
        daily_records_by_window: dict[str, list[dict[str, Any]]] = {
            window.window_id: [] for window in target_windows
        }
        target_windows_by_symbol: dict[str, list[ReplayTargetWindow]] = {}
        for window in target_windows:
            target_windows_by_symbol.setdefault(window.symbol, []).append(window)

        for trade_date in sorted({permission.trade_date for permission in permissions}):
            runner._apply_pending_fills(
                trade_date=trade_date,
                current_positions=current_positions,
                pending_signals_by_fill_date=pending_signals_by_fill_date,
                pending_buy_symbols=pending_buy_symbols,
                pending_sell_symbols=pending_sell_symbols,
            )
            daily_signals = strategy.generate_signals(
                trade_date=trade_date,
                bars_by_symbol=bars_by_symbol,
                permissions=permissions,
                assignments=assignments,
                current_positions=dict(current_positions),
                blocked_buy_symbols=set(pending_buy_symbols),
                blocked_sell_symbols=set(pending_sell_symbols),
            )
            signals.extend(daily_signals)

            for symbol, windows in target_windows_by_symbol.items():
                symbol_bars = strategy._bars_until_date(bars_by_symbol.get(symbol, []), trade_date)
                if not symbol_bars:
                    continue
                assignment = assignment_lookup.get((trade_date, symbol))
                permission = strategy._permission_for_date(permissions, trade_date)
                filters = strategy.trend_filters.evaluate(symbol_bars)
                entries = strategy.entry_rules.evaluate(symbol_bars)
                emitted = [signal.action for signal in daily_signals if signal.symbol == symbol]
                for window in windows:
                    if not self._in_observation_range(
                        trade_date=trade_date,
                        window=window,
                        lookback_days=lookback_days,
                    ):
                        continue
                    holding = None
                    exit_decision = None
                    position_qty = int(current_positions.get(symbol, 0))
                    if position_qty > 0 and assignment is not None:
                        holding = strategy.holding_engine.evaluate(symbol_bars, assignment, permission)
                        exit_decision = strategy.exit_guard.evaluate(
                            symbol_bars,
                            assignment,
                            permission,
                            holding,
                        )
                    daily_records_by_window[window.window_id].append(
                        {
                            "trade_date": trade_date.isoformat(),
                            "symbol": symbol,
                            "position_qty": position_qty,
                            "pending_buy": symbol in pending_buy_symbols,
                            "pending_sell": symbol in pending_sell_symbols,
                            "permission_allowed": permission.is_attack_allowed,
                            "approved_sector_id": permission.approved_sector_id,
                            "assignment_layer": assignment.layer if assignment is not None else None,
                            "assignment_score": round(assignment.layer_score, 6) if assignment is not None else None,
                            "assignment_reason": assignment.reason if assignment is not None else "missing_assignment",
                            "passed_filters": [
                                item.filter_name for item in filters if item.passed
                            ],
                            "triggered_entries": [
                                item.rule_name for item in entries if item.triggered
                            ],
                            "holding_should_hold": holding.should_hold if holding is not None else None,
                            "holding_health_score": (
                                round(holding.health_score, 6) if holding is not None else None
                            ),
                            "exit_should_exit": exit_decision.should_exit if exit_decision is not None else None,
                            "exit_category": exit_decision.category if exit_decision is not None else None,
                            "exit_reason": exit_decision.reason if exit_decision is not None else None,
                            "emitted_actions": emitted,
                        }
                    )
            runner._schedule_pending_fills(
                bars_by_symbol=bars_by_symbol,
                signals=daily_signals,
                pending_signals_by_fill_date=pending_signals_by_fill_date,
                pending_buy_symbols=pending_buy_symbols,
                pending_sell_symbols=pending_sell_symbols,
            )

        backtest_result = runner.engine.run(dataset_pack.bars, signals)
        window_breakdown = {
            str(item["window_id"]): item
            for item in mainline_window_breakdown(backtest_result.closed_trades, list(target_windows))
        }
        intervals_by_symbol = self._build_position_intervals(backtest_result.fills)
        rejected_by_symbol = self._group_rejections(backtest_result.rejected_signals)

        records: list[dict[str, Any]] = []
        for window in target_windows:
            window_details = window_breakdown.get(window.window_id, {})
            symbol_intervals = intervals_by_symbol.get(window.symbol, [])
            overlapping_intervals = [
                interval
                for interval in symbol_intervals
                if self._interval_overlaps_window(interval=interval, window=window)
            ]
            active_interval = min(
                overlapping_intervals,
                key=lambda item: item["entry_date"],
                default=None,
            )
            daily_records = daily_records_by_window.get(window.window_id, [])
            classification = self._classify_window_behavior(
                window=window,
                active_interval=active_interval,
                daily_records=daily_records,
            )
            records.append(
                {
                    "dataset_name": dataset_pack.dataset_name,
                    "candidate_name": candidate.candidate_name,
                    "strategy_name": strategy_name,
                    "window_id": window.window_id,
                    "symbol": window.symbol,
                    "start_date": window.start_date.isoformat(),
                    "end_date": window.end_date.isoformat(),
                    "capturable_return": round(window.capturable_return, 6),
                    "capture_ratio": round(float(window_details.get("capture_ratio", 0.0)), 6),
                    "missed": bool(window_details.get("missed", True)),
                    "classification": classification,
                    "active_interval": active_interval,
                    "buy_fills": [
                        self._serialize_fill(fill)
                        for fill in backtest_result.fills
                        if fill.symbol == window.symbol
                        and fill.action == "buy"
                        and window.start_date - timedelta(days=lookback_days) <= fill.trade_date <= window.end_date
                    ],
                    "sell_fills": [
                        self._serialize_fill(fill)
                        for fill in backtest_result.fills
                        if fill.symbol == window.symbol
                        and fill.action == "sell"
                        and window.start_date - timedelta(days=lookback_days) <= fill.trade_date <= window.end_date
                    ],
                    "rejected_signals": rejected_by_symbol.get(window.symbol, []),
                    "daily_records": daily_records,
                }
            )
        return records

    def _build_position_intervals(self, fills: list[Fill]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[Fill]] = {}
        for fill in sorted(fills, key=lambda item: (item.symbol, item.trade_date, item.action)):
            grouped.setdefault(fill.symbol, []).append(fill)

        intervals_by_symbol: dict[str, list[dict[str, Any]]] = {}
        for symbol, symbol_fills in grouped.items():
            quantity = 0
            interval_start: date | None = None
            intervals: list[dict[str, Any]] = []
            for fill in symbol_fills:
                if fill.action == "buy":
                    if quantity == 0:
                        interval_start = fill.trade_date
                    quantity += fill.quantity
                elif fill.action == "sell":
                    quantity -= fill.quantity
                    if quantity <= 0 and interval_start is not None:
                        intervals.append(
                            {
                                "entry_date": interval_start.isoformat(),
                                "exit_date": fill.trade_date.isoformat(),
                            }
                        )
                        interval_start = None
                        quantity = 0
            if quantity > 0 and interval_start is not None:
                intervals.append(
                    {
                        "entry_date": interval_start.isoformat(),
                        "exit_date": None,
                    }
                )
            intervals_by_symbol[symbol] = intervals
        return intervals_by_symbol

    def _group_rejections(self, rejected_signals: list[str]) -> dict[str, list[str]]:
        grouped: dict[str, list[str]] = {}
        for item in rejected_signals:
            parts = str(item).split(":")
            if len(parts) >= 2:
                grouped.setdefault(parts[1], []).append(str(item))
        return grouped

    def _classify_window_behavior(
        self,
        *,
        window: ReplayTargetWindow,
        active_interval: dict[str, Any] | None,
        daily_records: list[dict[str, Any]],
    ) -> str:
        if active_interval is None:
            emitted_buys = any("buy" in record["emitted_actions"] for record in daily_records)
            triggered_entries = any(record["triggered_entries"] for record in daily_records)
            if emitted_buys:
                return "signal_without_window_position"
            if triggered_entries:
                return "entry_triggered_but_no_window_position"
            return "no_entry"

        entry_date = date.fromisoformat(str(active_interval["entry_date"]))
        exit_date = (
            date.fromisoformat(str(active_interval["exit_date"]))
            if active_interval.get("exit_date") is not None
            else None
        )
        late_entry = entry_date > window.start_date
        early_exit = exit_date is not None and exit_date < window.end_date
        if late_entry and early_exit:
            return "late_entry_and_early_exit"
        if late_entry:
            return "late_entry"
        if early_exit:
            return "early_exit"
        return "held_through_window"

    def _build_comparisons(
        self,
        *,
        window_records: list[dict[str, Any]],
        incumbent_name: str,
        challenger_name: str,
    ) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
        for record in window_records:
            key = (str(record["strategy_name"]), str(record["window_id"]))
            grouped.setdefault(key, {})[str(record["candidate_name"])] = record

        comparisons: list[dict[str, Any]] = []
        for (strategy_name, window_id), pair in sorted(grouped.items()):
            incumbent = pair.get(incumbent_name)
            challenger = pair.get(challenger_name)
            if incumbent is None or challenger is None:
                continue
            issue = self._classify_pair_issue(incumbent=incumbent, challenger=challenger)
            comparisons.append(
                {
                    "strategy_name": strategy_name,
                    "window_id": window_id,
                    "symbol": incumbent["symbol"],
                    "issue": issue,
                    "incumbent_capture_ratio": incumbent["capture_ratio"],
                    "challenger_capture_ratio": challenger["capture_ratio"],
                    "capture_regression": round(
                        float(incumbent["capture_ratio"]) - float(challenger["capture_ratio"]),
                        6,
                    ),
                    "incumbent_classification": incumbent["classification"],
                    "challenger_classification": challenger["classification"],
                    "incumbent_interval": incumbent["active_interval"],
                    "challenger_interval": challenger["active_interval"],
                }
            )
        return comparisons

    def _classify_pair_issue(
        self,
        *,
        incumbent: dict[str, Any],
        challenger: dict[str, Any],
    ) -> str:
        incumbent_interval = incumbent.get("active_interval")
        challenger_interval = challenger.get("active_interval")
        if incumbent_interval is not None and challenger_interval is None:
            if challenger["classification"] == "no_entry":
                return "challenger_no_entry"
            return "challenger_no_window_position"
        if incumbent_interval is None:
            return "no_incumbent_advantage"
        incumbent_entry = date.fromisoformat(str(incumbent_interval["entry_date"]))
        challenger_entry = date.fromisoformat(str(challenger_interval["entry_date"])) if challenger_interval else None
        incumbent_exit = (
            date.fromisoformat(str(incumbent_interval["exit_date"]))
            if incumbent_interval.get("exit_date") is not None
            else None
        )
        challenger_exit = (
            date.fromisoformat(str(challenger_interval["exit_date"]))
            if challenger_interval and challenger_interval.get("exit_date") is not None
            else None
        )
        if challenger_entry is not None and challenger_entry > incumbent_entry:
            if challenger_exit is not None and (incumbent_exit is None or challenger_exit < incumbent_exit):
                return "challenger_late_entry_and_early_exit"
            return "challenger_late_entry"
        if (
            challenger_exit is not None
            and incumbent_exit is not None
            and challenger_exit < incumbent_exit
        ):
            return "challenger_early_exit"
        if challenger["classification"] != incumbent["classification"]:
            return "classification_mismatch"
        return "minor_or_mixed_difference"

    def _issue_summary(self, comparison_records: list[dict[str, Any]]) -> dict[str, int]:
        summary: dict[str, int] = {}
        for record in comparison_records:
            issue = str(record["issue"])
            summary[issue] = summary.get(issue, 0) + 1
        return dict(sorted(summary.items(), key=lambda item: (-item[1], item[0])))

    def _in_observation_range(
        self,
        *,
        trade_date: date,
        window: ReplayTargetWindow,
        lookback_days: int,
    ) -> bool:
        return window.start_date - timedelta(days=lookback_days) <= trade_date <= window.end_date

    def _interval_overlaps_window(
        self,
        *,
        interval: dict[str, Any],
        window: ReplayTargetWindow,
    ) -> bool:
        entry_date = date.fromisoformat(str(interval["entry_date"]))
        exit_date = (
            date.fromisoformat(str(interval["exit_date"]))
            if interval.get("exit_date") is not None
            else None
        )
        return entry_date <= window.end_date and (exit_date is None or exit_date >= window.start_date)

    def _serialize_fill(self, fill: Fill) -> dict[str, Any]:
        return {
            "trade_date": fill.trade_date.isoformat(),
            "symbol": fill.symbol,
            "action": fill.action,
            "quantity": fill.quantity,
            "price": round(fill.price, 6),
            "fees": round(fill.fees, 6),
        }


def write_window_replay_diagnostic(
    *,
    reports_dir: Path,
    report_name: str,
    result: WindowReplayDiagnosticResult,
    extras: dict[str, Any] | None = None,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    payload = result.as_dict()
    if extras:
        payload["extras"] = extras
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    return output_path
