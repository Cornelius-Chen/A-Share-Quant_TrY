from __future__ import annotations

from dataclasses import dataclass

from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.common.models import DailyBar, MainlineWindow, SectorSnapshot, StockSnapshot
from a_share_quant.strategy.experiment_runner import StrategyExperimentRunner, StrategySuiteResult


@dataclass(slots=True)
class DatasetPack:
    dataset_name: str
    config: dict[str, object]
    bars: list[DailyBar]
    index_bars: list[DailyBar] | None
    sector_snapshots: list[SectorSnapshot]
    stock_snapshots: list[StockSnapshot]
    mainline_windows: list[MainlineWindow]


@dataclass(slots=True)
class DatasetComparisonResult:
    suites: list[dict[str, object]]

    def comparison_rows(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for suite_entry in self.suites:
            suite = suite_entry["suite"]
            assert isinstance(suite, StrategySuiteResult)
            dataset_name = str(suite_entry["dataset_name"])
            for row in suite.comparison_rows():
                rows.append(
                    {
                        "dataset_name": dataset_name,
                        "strategy_name": row["strategy_name"],
                        "summary": row["summary"],
                        "signal_count": row["signal_count"],
                        "segment_count": row["segment_count"],
                        "permission_count": row["permission_count"],
                        "trade_overview": row["trade_overview"],
                        "segment_overview": row["segment_overview"],
                        "window_breakdown": row["window_breakdown"],
                    }
                )
        self._attach_ranks(rows, "total_return", reverse=True)
        self._attach_ranks(rows, "mainline_capture_ratio", reverse=True)
        self._attach_ranks(rows, "max_drawdown", reverse=False)
        return rows

    def aggregate_summary(self) -> dict[str, object]:
        rows = self.comparison_rows()
        best_total_return = max(rows, key=lambda item: float(item["summary"]["total_return"]))
        best_capture = max(rows, key=lambda item: float(item["summary"]["mainline_capture_ratio"]))
        lowest_drawdown = min(rows, key=lambda item: float(item["summary"]["max_drawdown"]))
        return {
            "comparison_count": len(rows),
            "dataset_count": len({row["dataset_name"] for row in rows}),
            "best_total_return": {
                "dataset_name": best_total_return["dataset_name"],
                "strategy_name": best_total_return["strategy_name"],
            },
            "best_capture": {
                "dataset_name": best_capture["dataset_name"],
                "strategy_name": best_capture["strategy_name"],
            },
            "lowest_drawdown": {
                "dataset_name": lowest_drawdown["dataset_name"],
                "strategy_name": lowest_drawdown["strategy_name"],
            },
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


class DatasetComparisonRunner:
    """Compare strategy-family suites across multiple dataset packs."""

    def __init__(self, *, engine: BacktestEngine) -> None:
        self.engine = engine

    def run(
        self,
        *,
        strategy_names: list[str],
        dataset_packs: list[DatasetPack],
    ) -> DatasetComparisonResult:
        suites: list[dict[str, object]] = []
        for dataset in dataset_packs:
            runner = StrategyExperimentRunner.from_config(
                engine=self.engine,
                config=dataset.config,
            )
            suite = runner.run_suite(
                strategy_names=strategy_names,
                bars=dataset.bars,
                index_bars=dataset.index_bars,
                sector_snapshots=dataset.sector_snapshots,
                stock_snapshots=dataset.stock_snapshots,
                mainline_windows=dataset.mainline_windows,
            )
            suites.append(
                {
                    "dataset_name": dataset.dataset_name,
                    "suite": suite,
                }
            )
        return DatasetComparisonResult(suites=suites)
