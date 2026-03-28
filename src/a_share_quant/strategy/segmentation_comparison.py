from __future__ import annotations

from dataclasses import dataclass

from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.common.models import DailyBar, MainlineWindow, SectorSnapshot, StockSnapshot
from a_share_quant.strategy.experiment_runner import StrategyExperimentResult, StrategyExperimentRunner


@dataclass(slots=True)
class SegmentationComparisonResult:
    results: list[dict[str, object]]

    def comparison_rows(self) -> list[dict[str, object]]:
        rows = []
        for item in self.results:
            experiment = item["experiment"]
            assert isinstance(experiment, StrategyExperimentResult)
            rows.append(
                {
                    "segmentation_method": item["segmentation_method"],
                    "strategy_name": experiment.strategy_name,
                    "summary": experiment.backtest_result.summary,
                    "segment_overview": experiment.segment_overview,
                    "trade_overview": experiment.trade_overview,
                    "window_breakdown": experiment.window_breakdown,
                    "signal_count": len(experiment.signals),
                    "segment_count": len(experiment.segments),
                    "permission_count": len(experiment.permissions),
                }
            )
        self._attach_ranks(rows, "total_return", reverse=True)
        self._attach_ranks(rows, "mainline_capture_ratio", reverse=True)
        self._attach_ranks(rows, "max_drawdown", reverse=False)
        return rows

    def aggregate_summary(self) -> dict[str, object]:
        rows = self.comparison_rows()
        return {
            "comparison_count": len(rows),
            "best_total_return_method": max(
                rows,
                key=lambda item: float(item["summary"]["total_return"]),
            )["segmentation_method"],
            "best_capture_method": max(
                rows,
                key=lambda item: float(item["summary"]["mainline_capture_ratio"]),
            )["segmentation_method"],
            "lowest_drawdown_method": min(
                rows,
                key=lambda item: float(item["summary"]["max_drawdown"]),
            )["segmentation_method"],
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


class SegmentationComparisonRunner:
    """Compare one strategy family across multiple segmentation methods under one config."""

    def __init__(self, *, engine: BacktestEngine, config: dict[str, object]) -> None:
        self.engine = engine
        self.config = config

    def run(
        self,
        *,
        strategy_name: str,
        segmentation_methods: list[str],
        bars: list[DailyBar],
        index_bars: list[DailyBar] | None,
        sector_snapshots: list[SectorSnapshot],
        stock_snapshots: list[StockSnapshot],
        mainline_windows: list[MainlineWindow],
    ) -> SegmentationComparisonResult:
        results: list[dict[str, object]] = []
        for segmentation_method in segmentation_methods:
            runner = StrategyExperimentRunner.from_config(
                engine=self.engine,
                config=self.config,
                segmentation_method_override=segmentation_method,
            )
            experiment = runner.run(
                strategy_name=strategy_name,
                bars=bars,
                index_bars=index_bars,
                sector_snapshots=sector_snapshots,
                stock_snapshots=stock_snapshots,
                mainline_windows=mainline_windows,
            )
            results.append(
                {
                    "segmentation_method": segmentation_method,
                    "experiment": experiment,
                }
            )
        return SegmentationComparisonResult(results=results)
