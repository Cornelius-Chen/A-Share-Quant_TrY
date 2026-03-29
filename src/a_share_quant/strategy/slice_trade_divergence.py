from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.common.config import merge_config
from a_share_quant.common.models import DailyBar, MainlineWindow, SectorSnapshot, StockSnapshot
from a_share_quant.strategy.dataset_comparison import DatasetPack
from a_share_quant.strategy.experiment_runner import StrategyExperimentRunner, StrategyExperimentResult
from a_share_quant.strategy.rule_sweep import RuleCandidate
from a_share_quant.strategy.time_slice_validation import ValidationSlice


@dataclass(slots=True)
class SliceTradeDivergenceReport:
    summary: dict[str, Any]
    strategy_symbol_summary: list[dict[str, Any]]
    worst_symbol_rows: list[dict[str, Any]]
    trade_pair_samples: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "strategy_symbol_summary": self.strategy_symbol_summary,
            "worst_symbol_rows": self.worst_symbol_rows,
            "trade_pair_samples": self.trade_pair_samples,
        }


class SliceTradeDivergenceAnalyzer:
    """Compare trade-level behavior between two candidates inside one slice."""

    def analyze(
        self,
        *,
        engine: BacktestEngine,
        dataset_pack: DatasetPack,
        validation_slice: ValidationSlice,
        strategy_names: list[str],
        incumbent: RuleCandidate,
        challenger: RuleCandidate,
    ) -> SliceTradeDivergenceReport:
        sliced_pack = self._slice_dataset_pack(dataset_pack, validation_slice)
        incumbent_results = self._run_candidate(
            engine=engine,
            dataset_pack=sliced_pack,
            strategy_names=strategy_names,
            candidate=incumbent,
        )
        challenger_results = self._run_candidate(
            engine=engine,
            dataset_pack=sliced_pack,
            strategy_names=strategy_names,
            candidate=challenger,
        )

        strategy_symbol_summary: list[dict[str, Any]] = []
        trade_pair_samples: list[dict[str, Any]] = []
        for strategy_name in strategy_names:
            incumbent_result = incumbent_results[strategy_name]
            challenger_result = challenger_results[strategy_name]
            strategy_symbol_summary.extend(
                self._symbol_summary_rows(
                    strategy_name=strategy_name,
                    incumbent_result=incumbent_result,
                    challenger_result=challenger_result,
                )
            )
            trade_pair_samples.extend(
                self._sample_trade_pairs(
                    strategy_name=strategy_name,
                    incumbent_result=incumbent_result,
                    challenger_result=challenger_result,
                )
            )

        worst_symbol_rows = sorted(
            strategy_symbol_summary,
            key=lambda item: (
                float(item["pnl_delta"]),
                -float(item["challenger_max_holding_days"]),
            ),
        )[:12]
        summary = {
            "dataset_name": dataset_pack.dataset_name,
            "slice_name": validation_slice.slice_name,
            "slice_start": validation_slice.start_date.isoformat(),
            "slice_end": validation_slice.end_date.isoformat(),
            "strategy_count": len(strategy_names),
            "symbol_row_count": len(strategy_symbol_summary),
            "weakest_symbol_row": worst_symbol_rows[0] if worst_symbol_rows else None,
            "interpretation": [
                "Negative pnl_delta rows show where the challenger realizes worse trade outcomes than the incumbent.",
                "Rows with equal capture but worse pnl are especially useful for diagnosing path-quality and drawdown issues.",
                "If the same symbol repeats across strategies, it is likely a real structural driver of the slice-level gap.",
            ],
        }
        return SliceTradeDivergenceReport(
            summary=summary,
            strategy_symbol_summary=strategy_symbol_summary,
            worst_symbol_rows=worst_symbol_rows,
            trade_pair_samples=trade_pair_samples[:24],
        )

    def _run_candidate(
        self,
        *,
        engine: BacktestEngine,
        dataset_pack: DatasetPack,
        strategy_names: list[str],
        candidate: RuleCandidate,
    ) -> dict[str, StrategyExperimentResult]:
        merged_config = merge_config(dataset_pack.config, candidate.override)
        runner = StrategyExperimentRunner.from_config(engine=engine, config=merged_config)
        return {
            strategy_name: runner.run(
                strategy_name=strategy_name,
                bars=dataset_pack.bars,
                index_bars=dataset_pack.index_bars,
                sector_snapshots=dataset_pack.sector_snapshots,
                stock_snapshots=dataset_pack.stock_snapshots,
                mainline_windows=dataset_pack.mainline_windows,
            )
            for strategy_name in strategy_names
        }

    def _symbol_summary_rows(
        self,
        *,
        strategy_name: str,
        incumbent_result: StrategyExperimentResult,
        challenger_result: StrategyExperimentResult,
    ) -> list[dict[str, Any]]:
        incumbent_by_symbol = self._group_trades_by_symbol(incumbent_result)
        challenger_by_symbol = self._group_trades_by_symbol(challenger_result)
        symbols = sorted(set(incumbent_by_symbol) | set(challenger_by_symbol))
        rows: list[dict[str, Any]] = []
        for symbol in symbols:
            incumbent_trades = incumbent_by_symbol.get(symbol, [])
            challenger_trades = challenger_by_symbol.get(symbol, [])
            rows.append(
                {
                    "strategy_name": strategy_name,
                    "symbol": symbol,
                    "incumbent_trade_count": len(incumbent_trades),
                    "challenger_trade_count": len(challenger_trades),
                    "incumbent_total_pnl": round(sum(item["pnl"] for item in incumbent_trades), 6),
                    "challenger_total_pnl": round(sum(item["pnl"] for item in challenger_trades), 6),
                    "pnl_delta": round(
                        sum(item["pnl"] for item in challenger_trades)
                        - sum(item["pnl"] for item in incumbent_trades),
                        6,
                    ),
                    "incumbent_avg_holding_days": round(
                        sum(item["holding_days"] for item in incumbent_trades) / len(incumbent_trades),
                        6,
                    )
                    if incumbent_trades
                    else 0.0,
                    "challenger_avg_holding_days": round(
                        sum(item["holding_days"] for item in challenger_trades) / len(challenger_trades),
                        6,
                    )
                    if challenger_trades
                    else 0.0,
                    "challenger_max_holding_days": max(
                        [item["holding_days"] for item in challenger_trades],
                        default=0,
                    ),
                }
            )
        return rows

    def _sample_trade_pairs(
        self,
        *,
        strategy_name: str,
        incumbent_result: StrategyExperimentResult,
        challenger_result: StrategyExperimentResult,
    ) -> list[dict[str, Any]]:
        incumbent_by_symbol = self._group_trades_by_symbol(incumbent_result)
        challenger_by_symbol = self._group_trades_by_symbol(challenger_result)
        samples: list[dict[str, Any]] = []
        for symbol in sorted(set(incumbent_by_symbol) | set(challenger_by_symbol)):
            incumbent_trades = incumbent_by_symbol.get(symbol, [])
            challenger_trades = challenger_by_symbol.get(symbol, [])
            for index in range(max(len(incumbent_trades), len(challenger_trades))):
                incumbent_trade = incumbent_trades[index] if index < len(incumbent_trades) else None
                challenger_trade = challenger_trades[index] if index < len(challenger_trades) else None
                if incumbent_trade is None and challenger_trade is None:
                    continue
                pnl_delta = round(
                    (float(challenger_trade["pnl"]) if challenger_trade is not None else 0.0)
                    - (float(incumbent_trade["pnl"]) if incumbent_trade is not None else 0.0),
                    6,
                )
                samples.append(
                    {
                        "strategy_name": strategy_name,
                        "symbol": symbol,
                        "trade_index": index,
                        "pnl_delta": pnl_delta,
                        "incumbent_trade": incumbent_trade,
                        "challenger_trade": challenger_trade,
                    }
                )
        return sorted(samples, key=lambda item: float(item["pnl_delta"]))[:24]

    def _group_trades_by_symbol(self, result: StrategyExperimentResult) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for trade in sorted(
            result.backtest_result.closed_trades,
            key=lambda item: (item.symbol, item.entry_date, item.exit_date),
        ):
            grouped.setdefault(trade.symbol, []).append(
                {
                    "entry_date": trade.entry_date.isoformat(),
                    "exit_date": trade.exit_date.isoformat(),
                    "quantity": trade.quantity,
                    "entry_price": round(trade.entry_price, 6),
                    "exit_price": round(trade.exit_price, 6),
                    "pnl": round(trade.pnl, 6),
                    "holding_days": trade.holding_days,
                }
            )
        return grouped

    def _slice_dataset_pack(
        self,
        dataset_pack: DatasetPack,
        validation_slice: ValidationSlice,
    ) -> DatasetPack:
        return DatasetPack(
            dataset_name=dataset_pack.dataset_name,
            config=dataset_pack.config,
            bars=self._filter_dated_records(dataset_pack.bars, validation_slice),
            index_bars=self._filter_dated_records(dataset_pack.index_bars or [], validation_slice),
            sector_snapshots=self._filter_dated_records(dataset_pack.sector_snapshots, validation_slice),
            stock_snapshots=self._filter_dated_records(dataset_pack.stock_snapshots, validation_slice),
            mainline_windows=self._filter_windows(dataset_pack.mainline_windows, validation_slice),
        )

    def _filter_dated_records(
        self,
        records: list[DailyBar] | list[SectorSnapshot] | list[StockSnapshot],
        validation_slice: ValidationSlice,
    ) -> list[DailyBar] | list[SectorSnapshot] | list[StockSnapshot]:
        return [
            record
            for record in records
            if validation_slice.start_date <= record.trade_date <= validation_slice.end_date
        ]

    def _filter_windows(
        self,
        windows: list[MainlineWindow],
        validation_slice: ValidationSlice,
    ) -> list[MainlineWindow]:
        return [
            window
            for window in windows
            if window.start_date >= validation_slice.start_date
            and window.end_date <= validation_slice.end_date
        ]


def write_slice_trade_divergence_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: SliceTradeDivergenceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
