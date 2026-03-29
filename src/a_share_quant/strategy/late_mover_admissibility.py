from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from a_share_quant.common.config import merge_config
from a_share_quant.common.models import MainlineWindow, Signal
from a_share_quant.strategy.dataset_comparison import DatasetPack
from a_share_quant.strategy.experiment_runner import StrategyExperimentRunner
from a_share_quant.strategy.rule_sweep import RuleCandidate


@dataclass(slots=True)
class CandidateAdmissibilityState:
    candidate_name: str
    window_breakdown_by_id: dict[str, dict[str, Any]]
    gap_records_by_window_id: dict[str, list[dict[str, Any]]]


@dataclass(slots=True)
class LateMoverAdmissibilityResult:
    summary: dict[str, Any]
    strategy_deltas: list[dict[str, Any]]
    top_window_gaps: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "strategy_deltas": self.strategy_deltas,
            "top_window_gaps": self.top_window_gaps,
        }


class LateMoverAdmissibilityAnalyzer:
    """Quantify windows where admissible late-mover entries are blocked by junk assignments."""

    def analyze(
        self,
        *,
        dataset_pack: DatasetPack,
        strategy_names: list[str],
        candidates: list[RuleCandidate],
        incumbent_name: str,
        challenger_name: str,
        lookback_days: int,
        engine,
        top_k: int = 20,
    ) -> LateMoverAdmissibilityResult:
        candidate_states: dict[tuple[str, str], CandidateAdmissibilityState] = {}
        for candidate in candidates:
            merged_config = merge_config(dataset_pack.config, candidate.override)
            runner = StrategyExperimentRunner.from_config(engine=engine, config=merged_config)
            for strategy_name in strategy_names:
                candidate_states[(candidate.candidate_name, strategy_name)] = self._collect_candidate_state(
                    dataset_pack=dataset_pack,
                    runner=runner,
                    candidate_name=candidate.candidate_name,
                    strategy_name=strategy_name,
                    lookback_days=lookback_days,
                )

        strategy_deltas: list[dict[str, Any]] = []
        top_window_gaps: list[dict[str, Any]] = []
        for strategy_name in strategy_names:
            incumbent_state = candidate_states.get((incumbent_name, strategy_name))
            challenger_state = candidate_states.get((challenger_name, strategy_name))
            if incumbent_state is None or challenger_state is None:
                continue
            strategy_delta, impacted_windows = self._compare_strategy(
                strategy_name=strategy_name,
                windows=dataset_pack.mainline_windows,
                incumbent_state=incumbent_state,
                challenger_state=challenger_state,
            )
            strategy_deltas.append(strategy_delta)
            top_window_gaps.extend(impacted_windows)

        top_window_gaps = sorted(
            top_window_gaps,
            key=lambda item: (-float(item["capture_regression"]), -float(item["max_gap_late_score"])),
        )[:top_k]
        summary = self._build_summary(
            dataset_name=dataset_pack.dataset_name,
            strategy_deltas=strategy_deltas,
            top_window_gaps=top_window_gaps,
            incumbent_name=incumbent_name,
            challenger_name=challenger_name,
        )
        return LateMoverAdmissibilityResult(
            summary=summary,
            strategy_deltas=strategy_deltas,
            top_window_gaps=top_window_gaps,
        )

    def _collect_candidate_state(
        self,
        *,
        dataset_pack: DatasetPack,
        runner: StrategyExperimentRunner,
        candidate_name: str,
        strategy_name: str,
        lookback_days: int,
    ) -> CandidateAdmissibilityState:
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

        windows_by_symbol: dict[str, list[MainlineWindow]] = {}
        for window in dataset_pack.mainline_windows:
            windows_by_symbol.setdefault(window.symbol, []).append(window)
        gap_records_by_window_id: dict[str, list[dict[str, Any]]] = {
            window.window_id: [] for window in dataset_pack.mainline_windows
        }

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

            emitted_symbols = {signal.symbol for signal in daily_signals if signal.action == "buy"}
            for symbol, windows in windows_by_symbol.items():
                symbol_bars = strategy._bars_until_date(bars_by_symbol.get(symbol, []), trade_date)
                if not symbol_bars:
                    continue
                assignment = assignment_lookup.get((trade_date, symbol))
                permission = strategy._permission_for_date(permissions, trade_date)
                if assignment is None or not permission.is_attack_allowed:
                    continue
                if assignment.sector_id != permission.approved_sector_id:
                    continue

                filters = strategy.trend_filters.evaluate(symbol_bars)
                entries = strategy.entry_rules.evaluate(symbol_bars)
                if not any(item.passed for item in filters) or not any(item.triggered for item in entries):
                    continue
                if assignment.layer != "junk":
                    continue

                gap_record = {
                    "trade_date": trade_date.isoformat(),
                    "assignment_reason": assignment.reason,
                    "layer_score": round(assignment.layer_score, 6),
                    "late_score": round(assignment.late_score, 6),
                    "leader_score": round(assignment.leader_score, 6),
                    "core_score": round(assignment.core_score, 6),
                    "passed_filters": [item.filter_name for item in filters if item.passed],
                    "triggered_entries": [item.rule_name for item in entries if item.triggered],
                    "emitted_buy_signal": symbol in emitted_symbols,
                }
                for window in windows:
                    if self._in_observation_range(
                        trade_date=trade_date,
                        window=window,
                        lookback_days=lookback_days,
                    ):
                        gap_records_by_window_id[window.window_id].append(gap_record)

            runner._schedule_pending_fills(
                bars_by_symbol=bars_by_symbol,
                signals=daily_signals,
                pending_signals_by_fill_date=pending_signals_by_fill_date,
                pending_buy_symbols=pending_buy_symbols,
                pending_sell_symbols=pending_sell_symbols,
            )

        window_breakdown_by_id = {
            str(item["window_id"]): item
            for item in runner.run(
                strategy_name=strategy_name,
                bars=dataset_pack.bars,
                index_bars=dataset_pack.index_bars,
                sector_snapshots=dataset_pack.sector_snapshots,
                stock_snapshots=dataset_pack.stock_snapshots,
                mainline_windows=dataset_pack.mainline_windows,
            ).window_breakdown
        }
        return CandidateAdmissibilityState(
            candidate_name=candidate_name,
            window_breakdown_by_id=window_breakdown_by_id,
            gap_records_by_window_id=gap_records_by_window_id,
        )

    def _compare_strategy(
        self,
        *,
        strategy_name: str,
        windows: list[MainlineWindow],
        incumbent_state: CandidateAdmissibilityState,
        challenger_state: CandidateAdmissibilityState,
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        impacted_windows: list[dict[str, Any]] = []
        for window in windows:
            incumbent_window = incumbent_state.window_breakdown_by_id.get(window.window_id)
            challenger_window = challenger_state.window_breakdown_by_id.get(window.window_id)
            if incumbent_window is None or challenger_window is None:
                continue
            capture_regression = round(
                float(incumbent_window["capture_ratio"]) - float(challenger_window["capture_ratio"]),
                6,
            )
            gap_records = challenger_state.gap_records_by_window_id.get(window.window_id, [])
            if capture_regression <= 0 or not gap_records:
                continue
            impacted_windows.append(
                {
                    "strategy_name": strategy_name,
                    "window_id": window.window_id,
                    "symbol": window.symbol,
                    "start_date": window.start_date.isoformat(),
                    "end_date": window.end_date.isoformat(),
                    "capturable_return": round(window.capturable_return, 6),
                    "incumbent_capture_ratio": round(float(incumbent_window["capture_ratio"]), 6),
                    "challenger_capture_ratio": round(float(challenger_window["capture_ratio"]), 6),
                    "capture_regression": capture_regression,
                    "gap_day_count": len(gap_records),
                    "first_gap_date": gap_records[0]["trade_date"],
                    "last_gap_date": gap_records[-1]["trade_date"],
                    "max_gap_layer_score": round(max(item["layer_score"] for item in gap_records), 6),
                    "max_gap_late_score": round(max(item["late_score"] for item in gap_records), 6),
                    "max_gap_core_score": round(max(item["core_score"] for item in gap_records), 6),
                    "assignment_reasons": sorted({str(item["assignment_reason"]) for item in gap_records}),
                    "triggered_entry_rules": sorted(
                        {
                            rule_name
                            for item in gap_records
                            for rule_name in item["triggered_entries"]
                        }
                    ),
                    "passed_filters": sorted(
                        {
                            filter_name
                            for item in gap_records
                            for filter_name in item["passed_filters"]
                        }
                    ),
                    "classification": (
                        "blocked_window"
                        if float(challenger_window["capture_ratio"]) == 0.0
                        else "partial_capture_with_admissibility_gap"
                    ),
                }
            )

        mean_capture_regression = round(
            sum(item["capture_regression"] for item in impacted_windows) / len(impacted_windows),
            6,
        ) if impacted_windows else 0.0
        strategy_delta = {
            "strategy_name": strategy_name,
            "impacted_window_count": len(impacted_windows),
            "blocked_window_count": sum(
                1 for item in impacted_windows if item["classification"] == "blocked_window"
            ),
            "partial_window_count": sum(
                1
                for item in impacted_windows
                if item["classification"] == "partial_capture_with_admissibility_gap"
            ),
            "mean_capture_regression": mean_capture_regression,
            "worst_window": max(
                impacted_windows,
                key=lambda item: float(item["capture_regression"]),
                default=None,
            ),
        }
        return strategy_delta, impacted_windows

    def _build_summary(
        self,
        *,
        dataset_name: str,
        strategy_deltas: list[dict[str, Any]],
        top_window_gaps: list[dict[str, Any]],
        incumbent_name: str,
        challenger_name: str,
    ) -> dict[str, Any]:
        mean_capture_regression = round(
            sum(item["mean_capture_regression"] for item in strategy_deltas) / len(strategy_deltas),
            6,
        ) if strategy_deltas else 0.0
        symbol_count = len({str(item["symbol"]) for item in top_window_gaps})
        blocked_window_count = sum(
            1 for item in top_window_gaps if item["classification"] == "blocked_window"
        )
        partial_window_count = sum(
            1
            for item in top_window_gaps
            if item["classification"] == "partial_capture_with_admissibility_gap"
        )
        return {
            "dataset_name": dataset_name,
            "incumbent_name": incumbent_name,
            "challenger_name": challenger_name,
            "strategy_count": len(strategy_deltas),
            "impacted_window_count": len(top_window_gaps),
            "impacted_symbol_count": symbol_count,
            "blocked_window_count": blocked_window_count,
            "partial_window_count": partial_window_count,
            "mean_capture_regression": mean_capture_regression,
            "worst_strategy": max(
                strategy_deltas,
                key=lambda item: float(item["mean_capture_regression"]),
                default=None,
            ),
            "worst_window": max(
                top_window_gaps,
                key=lambda item: float(item["capture_regression"]),
                default=None,
            ),
        }

    def _in_observation_range(
        self,
        *,
        trade_date: date,
        window: MainlineWindow,
        lookback_days: int,
    ) -> bool:
        return window.start_date - timedelta(days=lookback_days) <= trade_date <= window.end_date


def write_late_mover_admissibility_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: LateMoverAdmissibilityResult,
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
