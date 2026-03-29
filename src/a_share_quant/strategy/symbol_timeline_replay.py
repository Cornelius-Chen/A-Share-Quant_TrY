from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.common.config import merge_config
from a_share_quant.common.models import AttackPermission, DailyBar, SectorSnapshot, StockSnapshot
from a_share_quant.strategy.dataset_comparison import DatasetPack
from a_share_quant.strategy.experiment_runner import StrategyExperimentRunner
from a_share_quant.strategy.rule_sweep import RuleCandidate


@dataclass(slots=True)
class SymbolTimelineReplayReport:
    summary: dict[str, Any]
    candidate_records: list[dict[str, Any]]
    comparison_records: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_records": self.candidate_records,
            "comparison_records": self.comparison_records,
        }


class SymbolTimelineReplay:
    """Replay one symbol across a fixed date range for a few candidates."""

    def analyze(
        self,
        *,
        dataset_pack: DatasetPack,
        strategy_names: list[str],
        candidates: list[RuleCandidate],
        symbol: str,
        start_date: date,
        end_date: date,
        incumbent_name: str,
        challenger_name: str,
        engine: BacktestEngine,
    ) -> SymbolTimelineReplayReport:
        candidate_records: list[dict[str, Any]] = []
        for candidate in candidates:
            merged_config = merge_config(dataset_pack.config, candidate.override)
            runner = StrategyExperimentRunner.from_config(engine=engine, config=merged_config)
            for strategy_name in strategy_names:
                candidate_records.append(
                    self._analyze_candidate_strategy(
                        dataset_pack=dataset_pack,
                        runner=runner,
                        candidate=candidate,
                        strategy_name=strategy_name,
                        symbol=symbol,
                        start_date=start_date,
                        end_date=end_date,
                    )
                )

        comparison_records = self._build_comparisons(
            candidate_records=candidate_records,
            incumbent_name=incumbent_name,
            challenger_name=challenger_name,
        )
        summary = {
            "dataset_name": dataset_pack.dataset_name,
            "symbol": symbol,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "strategy_count": len(strategy_names),
            "candidate_count": len(candidates),
            "comparison_count": len(comparison_records),
        }
        return SymbolTimelineReplayReport(
            summary=summary,
            candidate_records=candidate_records,
            comparison_records=comparison_records,
        )

    def _analyze_candidate_strategy(
        self,
        *,
        dataset_pack: DatasetPack,
        runner: StrategyExperimentRunner,
        candidate: RuleCandidate,
        strategy_name: str,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> dict[str, Any]:
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
        pending_signals_by_fill_date: dict[date, list] = {}
        pending_buy_symbols: set[str] = set()
        pending_sell_symbols: set[str] = set()
        signals: list = []
        daily_records: list[dict[str, Any]] = []

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

            if start_date <= trade_date <= end_date:
                symbol_bars = strategy._bars_until_date(bars_by_symbol.get(symbol, []), trade_date)
                assignment = assignment_lookup.get((trade_date, symbol))
                permission = strategy._permission_for_date(permissions, trade_date)
                filters = strategy.trend_filters.evaluate(symbol_bars) if symbol_bars else []
                entries = strategy.entry_rules.evaluate(symbol_bars) if symbol_bars else []
                holding = None
                exit_decision = None
                position_qty = int(current_positions.get(symbol, 0))
                if position_qty > 0 and assignment is not None and symbol_bars:
                    holding = strategy.holding_engine.evaluate(symbol_bars, assignment, permission)
                    exit_decision = strategy.exit_guard.evaluate(
                        symbol_bars,
                        assignment,
                        permission,
                        holding,
                    )
                daily_records.append(
                    {
                        "trade_date": trade_date.isoformat(),
                        "position_qty": position_qty,
                        "pending_buy": symbol in pending_buy_symbols,
                        "pending_sell": symbol in pending_sell_symbols,
                        "permission_allowed": permission.is_attack_allowed,
                        "approved_sector_id": permission.approved_sector_id,
                        "assignment_layer": assignment.layer if assignment is not None else None,
                        "assignment_score": round(assignment.layer_score, 6) if assignment is not None else None,
                        "assignment_reason": assignment.reason if assignment is not None else "missing_assignment",
                        "passed_filters": [item.filter_name for item in filters if item.passed],
                        "triggered_entries": [item.rule_name for item in entries if item.triggered],
                        "holding_should_hold": holding.should_hold if holding is not None else None,
                        "holding_health_score": round(holding.health_score, 6) if holding is not None else None,
                        "exit_should_exit": exit_decision.should_exit if exit_decision is not None else None,
                        "exit_category": exit_decision.category if exit_decision is not None else None,
                        "exit_reason": exit_decision.reason if exit_decision is not None else None,
                        "emitted_actions": [signal.action for signal in daily_signals if signal.symbol == symbol],
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
        symbol_fills = [
            self._serialize_fill(fill)
            for fill in backtest_result.fills
            if fill.symbol == symbol and start_date <= fill.trade_date <= end_date
        ]
        symbol_trades = [
            self._serialize_trade(trade)
            for trade in backtest_result.closed_trades
            if trade.symbol == symbol
            and not (trade.exit_date < start_date or trade.entry_date > end_date)
        ]
        return {
            "candidate_name": candidate.candidate_name,
            "strategy_name": strategy_name,
            "symbol": symbol,
            "daily_records": daily_records,
            "fills": symbol_fills,
            "closed_trades": symbol_trades,
        }

    def _build_comparisons(
        self,
        *,
        candidate_records: list[dict[str, Any]],
        incumbent_name: str,
        challenger_name: str,
    ) -> list[dict[str, Any]]:
        grouped: dict[str, dict[str, dict[str, Any]]] = {}
        for record in candidate_records:
            grouped.setdefault(str(record["strategy_name"]), {})[str(record["candidate_name"])] = record

        comparisons: list[dict[str, Any]] = []
        for strategy_name, candidates in sorted(grouped.items()):
            incumbent = candidates.get(incumbent_name)
            challenger = candidates.get(challenger_name)
            if incumbent is None or challenger is None:
                continue
            comparisons.append(
                {
                    "strategy_name": strategy_name,
                    "incumbent_fill_count": len(incumbent["fills"]),
                    "challenger_fill_count": len(challenger["fills"]),
                    "incumbent_trade_count": len(incumbent["closed_trades"]),
                    "challenger_trade_count": len(challenger["closed_trades"]),
                    "incumbent_total_pnl": round(
                        sum(float(item["pnl"]) for item in incumbent["closed_trades"]),
                        6,
                    ),
                    "challenger_total_pnl": round(
                        sum(float(item["pnl"]) for item in challenger["closed_trades"]),
                        6,
                    ),
                    "pnl_delta": round(
                        sum(float(item["pnl"]) for item in challenger["closed_trades"])
                        - sum(float(item["pnl"]) for item in incumbent["closed_trades"]),
                        6,
                    ),
                }
            )
        return comparisons

    def _serialize_fill(self, fill) -> dict[str, Any]:
        return {
            "trade_date": fill.trade_date.isoformat(),
            "action": fill.action,
            "quantity": fill.quantity,
            "price": round(fill.price, 6),
            "fees": round(fill.fees, 6),
        }

    def _serialize_trade(self, trade) -> dict[str, Any]:
        return {
            "entry_date": trade.entry_date.isoformat(),
            "exit_date": trade.exit_date.isoformat(),
            "quantity": trade.quantity,
            "entry_price": round(trade.entry_price, 6),
            "exit_price": round(trade.exit_price, 6),
            "pnl": round(trade.pnl, 6),
            "holding_days": trade.holding_days,
        }


def write_symbol_timeline_replay_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: SymbolTimelineReplayReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
