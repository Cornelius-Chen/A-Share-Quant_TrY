from __future__ import annotations

from dataclasses import dataclass

from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.backtest.metrics import (
    mainline_capture_ratio,
    mainline_window_breakdown,
    missed_mainline_count,
)
from a_share_quant.common.models import (
    AttackPermission,
    BacktestResult,
    DailyBar,
    MainlineSectorScore,
    MainlineWindow,
    SampleSegment,
    SectorSnapshot,
    Signal,
    StockSnapshot,
)
from a_share_quant.regime.attack_permission_engine import AttackPermissionConfig, AttackPermissionEngine
from a_share_quant.regime.mainline_sector_scorer import MainlineSectorScorer
from a_share_quant.regime.sample_segmenter import SampleSegmenter, SegmenterConfig
from a_share_quant.strategy.mainline_strategy_base import BaseMainlineTrendStrategy, StrategyConfig
from a_share_quant.strategy.mainline_trend_a import MainlineTrendA
from a_share_quant.strategy.mainline_trend_b import MainlineTrendB
from a_share_quant.strategy.mainline_trend_c import MainlineTrendC
from a_share_quant.trend.entry_rules import EntryRuleConfig, EntryRules
from a_share_quant.trend.exit_guard import ExitGuard, ExitGuardConfig
from a_share_quant.trend.holding_engine import HoldingConfig, HoldingEngine
from a_share_quant.trend.leader_hierarchy_ranker import HierarchyConfig, LeaderHierarchyRanker
from a_share_quant.trend.trend_filters import TrendFilterConfig, TrendFilters


@dataclass(slots=True)
class StrategyExperimentResult:
    strategy_name: str
    signals: list[Signal]
    sector_scores: list[MainlineSectorScore]
    segments: list[SampleSegment]
    permissions: list[AttackPermission]
    backtest_result: BacktestResult
    window_breakdown: list[dict[str, object]]
    segment_overview: dict[str, object]
    trade_overview: dict[str, object]


@dataclass(slots=True)
class StrategySuiteResult:
    results: list[StrategyExperimentResult]

    def comparison_rows(self) -> list[dict[str, object]]:
        rows = [
            {
                "strategy_name": result.strategy_name,
                "summary": result.backtest_result.summary,
                "signal_count": len(result.signals),
                "segment_count": len(result.segments),
                "permission_count": len(result.permissions),
                "fill_count": len(result.backtest_result.fills),
                "closed_trade_count": len(result.backtest_result.closed_trades),
                "segment_overview": result.segment_overview,
                "trade_overview": result.trade_overview,
                "window_breakdown": result.window_breakdown,
            }
            for result in self.results
        ]
        self._attach_ranks(rows, "total_return", reverse=True)
        self._attach_ranks(rows, "mainline_capture_ratio", reverse=True)
        self._attach_ranks(rows, "max_drawdown", reverse=False)
        return rows

    def aggregate_summary(self) -> dict[str, object]:
        rows = self.comparison_rows()
        return {
            "strategy_count": len(rows),
            "best_total_return_strategy": max(
                rows,
                key=lambda item: float(item["summary"]["total_return"]),
            )["strategy_name"],
            "best_capture_strategy": max(
                rows,
                key=lambda item: float(item["summary"]["mainline_capture_ratio"]),
            )["strategy_name"],
            "lowest_drawdown_strategy": min(
                rows,
                key=lambda item: float(item["summary"]["max_drawdown"]),
            )["strategy_name"],
        }

    def _attach_ranks(
        self,
        rows: list[dict[str, object]],
        metric_name: str,
        *,
        reverse: bool,
    ) -> None:
        sorted_rows = sorted(
            rows,
            key=lambda item: float(item["summary"][metric_name]),
            reverse=reverse,
        )
        for index, row in enumerate(sorted_rows, start=1):
            row.setdefault("ranks", {})[metric_name] = index


class StrategyExperimentRunner:
    """Generate strategy-family signals from regime/trend modules and run the backtest."""

    def __init__(
        self,
        *,
        engine: BacktestEngine,
        segmenter: SampleSegmenter | None = None,
        scorer: MainlineSectorScorer | None = None,
        permission_engine: AttackPermissionEngine | None = None,
        hierarchy_ranker: LeaderHierarchyRanker | None = None,
        strategy_config: StrategyConfig | None = None,
        trend_filters: TrendFilters | None = None,
        entry_rules: EntryRules | None = None,
        holding_engine: HoldingEngine | None = None,
        exit_guard: ExitGuard | None = None,
        segmentation_method: str = "sector_trend",
    ) -> None:
        self.engine = engine
        self.segmenter = segmenter or SampleSegmenter()
        self.scorer = scorer or MainlineSectorScorer()
        self.permission_engine = permission_engine or AttackPermissionEngine()
        self.hierarchy_ranker = hierarchy_ranker or LeaderHierarchyRanker()
        self.strategy_config = strategy_config or StrategyConfig()
        self.trend_filters = trend_filters or TrendFilters()
        self.entry_rules = entry_rules or EntryRules()
        self.holding_engine = holding_engine or HoldingEngine()
        self.exit_guard = exit_guard or ExitGuard()
        self.segmentation_method = segmentation_method

    @classmethod
    def from_config(
        cls,
        *,
        engine: BacktestEngine,
        config: dict[str, object],
        segmentation_method_override: str | None = None,
    ) -> "StrategyExperimentRunner":
        regime_config = config.get("regime", {})
        trend_config = config.get("trend", {})
        strategy_config = config.get("strategy", {})
        hierarchy_config = trend_config.get("hierarchy", {}) if isinstance(trend_config, dict) else {}
        filter_config = trend_config.get("filters", {}) if isinstance(trend_config, dict) else {}
        entry_config = trend_config.get("entry_rules", {}) if isinstance(trend_config, dict) else {}
        holding_config = trend_config.get("holding", {}) if isinstance(trend_config, dict) else {}
        exit_config = trend_config.get("exit_guard", {}) if isinstance(trend_config, dict) else {}

        return cls(
            engine=engine,
            segmenter=SampleSegmenter(
                SegmenterConfig(
                    min_segment_length=int(regime_config.get("min_segment_length", 2)),
                    index_window=int(regime_config.get("index_window", 2)),
                    index_min_return=float(regime_config.get("index_min_return", 0.01)),
                    sector_score_threshold=float(regime_config.get("sector_score_threshold", 4.0)),
                )
            ),
            scorer=MainlineSectorScorer(),
            permission_engine=AttackPermissionEngine(
                AttackPermissionConfig(
                    min_top_score=float(regime_config.get("min_top_score", 4.0)),
                    min_score_margin=float(regime_config.get("min_score_margin", 0.2)),
                    require_active_segment=True,
                )
            ),
            hierarchy_ranker=LeaderHierarchyRanker(
                HierarchyConfig(
                    min_resonance_for_core=float(hierarchy_config.get("min_resonance_for_core", 0.55)),
                    min_quality_for_late_mover=float(hierarchy_config.get("min_quality_for_late_mover", 0.55)),
                    min_composite_for_non_junk=float(hierarchy_config.get("min_composite_for_non_junk", 0.60)),
                )
            ),
            strategy_config=StrategyConfig(
                buy_quantity=int(strategy_config.get("buy_quantity", 100)),
            ),
            trend_filters=TrendFilters(
                TrendFilterConfig(
                    short_window=int(filter_config.get("short_window", 2)),
                    medium_window=int(filter_config.get("medium_window", 3)),
                    long_window=int(filter_config.get("long_window", 4)),
                    loose_window=int(filter_config.get("loose_window", 5)),
                    repair_window=int(filter_config.get("repair_window", 3)),
                )
            ),
            entry_rules=EntryRules(
                EntryRuleConfig(
                    confirmation_window=int(entry_config.get("confirmation_window", 2)),
                    medium_window=int(entry_config.get("medium_window", 3)),
                    breakout_lookback=int(entry_config.get("breakout_lookback", 4)),
                )
            ),
            holding_engine=HoldingEngine(
                HoldingConfig(
                    medium_window=int(holding_config.get("medium_window", 3)),
                    min_health_score_to_hold=float(holding_config.get("min_health_score_to_hold", 1.5)),
                )
            ),
            exit_guard=ExitGuard(
                ExitGuardConfig(
                    medium_window=int(exit_config.get("medium_window", 3)),
                )
            ),
            segmentation_method=segmentation_method_override
            or str(regime_config.get("segmentation_method", "sector_trend")),
        )

    def run(
        self,
        *,
        strategy_name: str,
        bars: list[DailyBar],
        index_bars: list[DailyBar] | None,
        sector_snapshots: list[SectorSnapshot],
        stock_snapshots: list[StockSnapshot],
        mainline_windows: list[MainlineWindow],
    ) -> StrategyExperimentResult:
        strategy = self._strategy_from_name(strategy_name)
        bars_by_symbol = self._bars_by_symbol(bars)
        sector_scores = self.scorer.score(sector_snapshots)
        segments = self._build_segments(
            sector_scores=sector_scores,
            index_bars=index_bars or [],
        )
        permissions = self.permission_engine.evaluate(sector_scores, segments)

        allowed_sector_ids = {
            permission.approved_sector_id
            for permission in permissions
            if permission.is_attack_allowed and permission.approved_sector_id is not None
        }
        assignments = self.hierarchy_ranker.rank(
            stock_snapshots,
            allowed_sector_ids=allowed_sector_ids or None,
        )

        current_positions: dict[str, int] = {}
        pending_signals_by_fill_date: dict[date, list[Signal]] = {}
        pending_buy_symbols: set[str] = set()
        pending_sell_symbols: set[str] = set()
        signals: list[Signal] = []
        for trade_date in sorted({permission.trade_date for permission in permissions}):
            self._apply_pending_fills(
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
            self._schedule_pending_fills(
                bars_by_symbol=bars_by_symbol,
                signals=daily_signals,
                pending_signals_by_fill_date=pending_signals_by_fill_date,
                pending_buy_symbols=pending_buy_symbols,
                pending_sell_symbols=pending_sell_symbols,
            )

        result = self.engine.run(bars, signals)
        result.summary["mainline_capture_ratio"] = round(
            mainline_capture_ratio(result.closed_trades, mainline_windows),
            6,
        )
        result.summary["missed_mainline_count"] = missed_mainline_count(
            result.closed_trades,
            mainline_windows,
        )
        result.summary["strategy_name"] = strategy_name
        result.summary["signal_count"] = len(signals)
        window_breakdown = mainline_window_breakdown(result.closed_trades, mainline_windows)

        return StrategyExperimentResult(
            strategy_name=strategy_name,
            signals=signals,
            sector_scores=sector_scores,
            segments=segments,
            permissions=permissions,
            backtest_result=result,
            window_breakdown=window_breakdown,
            segment_overview=self._segment_overview(segments, permissions),
            trade_overview=self._trade_overview(result),
        )

    def run_suite(
        self,
        *,
        strategy_names: list[str],
        bars: list[DailyBar],
        index_bars: list[DailyBar] | None,
        sector_snapshots: list[SectorSnapshot],
        stock_snapshots: list[StockSnapshot],
        mainline_windows: list[MainlineWindow],
    ) -> StrategySuiteResult:
        results = [
            self.run(
                strategy_name=strategy_name,
                bars=bars,
                index_bars=index_bars,
                sector_snapshots=sector_snapshots,
                stock_snapshots=stock_snapshots,
                mainline_windows=mainline_windows,
            )
            for strategy_name in strategy_names
        ]
        return StrategySuiteResult(results=results)

    def _strategy_from_name(self, strategy_name: str) -> BaseMainlineTrendStrategy:
        mapping: dict[str, type[BaseMainlineTrendStrategy]] = {
            "mainline_trend_a": MainlineTrendA,
            "mainline_trend_b": MainlineTrendB,
            "mainline_trend_c": MainlineTrendC,
        }
        try:
            return mapping[strategy_name](
                config=self.strategy_config,
                trend_filters=self.trend_filters,
                entry_rules=self.entry_rules,
                holding_engine=self.holding_engine,
                exit_guard=self.exit_guard,
            )
        except KeyError as exc:
            raise ValueError(f"Unsupported strategy name: {strategy_name}") from exc

    def _bars_by_symbol(self, bars: list[DailyBar]) -> dict[str, list[DailyBar]]:
        grouped: dict[str, list[DailyBar]] = {}
        for bar in sorted(bars, key=lambda item: (item.symbol, item.trade_date)):
            grouped.setdefault(bar.symbol, []).append(bar)
        return grouped

    def _schedule_pending_fills(
        self,
        *,
        bars_by_symbol: dict[str, list[DailyBar]],
        signals: list[Signal],
        pending_signals_by_fill_date: dict[date, list[Signal]],
        pending_buy_symbols: set[str],
        pending_sell_symbols: set[str],
    ) -> None:
        for signal in signals:
            fill_date = self._next_fill_date(signal, bars_by_symbol.get(signal.symbol, []))
            if fill_date is None:
                continue
            pending_signals_by_fill_date.setdefault(fill_date, []).append(signal)
            if signal.action == "buy":
                pending_buy_symbols.add(signal.symbol)
            elif signal.action == "sell":
                pending_sell_symbols.add(signal.symbol)

    def _apply_pending_fills(
        self,
        *,
        trade_date: date,
        current_positions: dict[str, int],
        pending_signals_by_fill_date: dict[date, list[Signal]],
        pending_buy_symbols: set[str],
        pending_sell_symbols: set[str],
    ) -> None:
        for signal in pending_signals_by_fill_date.pop(trade_date, []):
            if signal.action == "buy":
                current_positions[signal.symbol] = current_positions.get(signal.symbol, 0) + signal.quantity
                pending_buy_symbols.discard(signal.symbol)
            elif signal.action == "sell":
                remaining = current_positions.get(signal.symbol, 0) - signal.quantity
                if remaining > 0:
                    current_positions[signal.symbol] = remaining
                else:
                    current_positions.pop(signal.symbol, None)
                pending_sell_symbols.discard(signal.symbol)

    def _next_fill_date(self, signal: Signal, bars: list[DailyBar]) -> date | None:
        for bar in bars:
            if bar.trade_date > signal.trade_date:
                return bar.trade_date
        return None

    def _segment_overview(
        self,
        segments: list[SampleSegment],
        permissions: list[AttackPermission],
    ) -> dict[str, object]:
        active_days = sum(segment.length for segment in segments)
        approved_days = sum(1 for permission in permissions if permission.is_attack_allowed)
        return {
            "segmentation_method": self.segmentation_method,
            "segment_count": len(segments),
            "active_segment_days": active_days,
            "approved_days": approved_days,
            "approval_rate": round(approved_days / len(permissions), 6) if permissions else 0.0,
        }

    def _trade_overview(self, result: BacktestResult) -> dict[str, object]:
        trades = result.closed_trades
        avg_holding_days = (
            round(sum(trade.holding_days for trade in trades) / len(trades), 6)
            if trades
            else 0.0
        )
        total_realized_pnl = round(sum(trade.pnl for trade in trades), 6)
        symbols = sorted({trade.symbol for trade in trades})
        return {
            "avg_holding_days": avg_holding_days,
            "total_realized_pnl": total_realized_pnl,
            "traded_symbols": symbols,
        }

    def _build_segments(
        self,
        *,
        sector_scores: list[MainlineSectorScore],
        index_bars: list[DailyBar],
    ) -> list[SampleSegment]:
        if self.segmentation_method == "sector_trend":
            return self.segmenter.segment_by_sector_trend(sector_scores)
        if self.segmentation_method == "index_trend":
            if not index_bars:
                raise ValueError("index_bars are required when segmentation_method=index_trend")
            return self.segmenter.segment_by_index_trend(index_bars)
        if self.segmentation_method == "resonance":
            if not index_bars:
                raise ValueError("index_bars are required when segmentation_method=resonance")
            return self.segmenter.segment_by_resonance(index_bars, sector_scores)
        raise ValueError(f"Unsupported segmentation method: {self.segmentation_method}")
