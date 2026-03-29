from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.common.config import merge_config
from a_share_quant.common.models import DailyBar, MainlineWindow, SectorSnapshot, StockSnapshot
from a_share_quant.strategy.dataset_comparison import DatasetPack
from a_share_quant.strategy.experiment_runner import StrategyExperimentRunner, StrategySuiteResult
from a_share_quant.strategy.rule_sweep import RuleCandidate


@dataclass(frozen=True, slots=True)
class ValidationSlice:
    slice_name: str
    start_date: date
    end_date: date


@dataclass(slots=True)
class TimeSliceValidationResult:
    suites: list[dict[str, object]]

    def comparison_rows(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for suite_entry in self.suites:
            suite = suite_entry["suite"]
            assert isinstance(suite, StrategySuiteResult)
            dataset_name = str(suite_entry["dataset_name"])
            slice_name = str(suite_entry["slice_name"])
            slice_start = str(suite_entry["slice_start"])
            slice_end = str(suite_entry["slice_end"])
            candidate_name = str(suite_entry["candidate_name"])
            candidate_description = suite_entry.get("candidate_description")
            for row in suite.comparison_rows():
                rows.append(
                    {
                        "dataset_name": dataset_name,
                        "slice_name": slice_name,
                        "slice_start": slice_start,
                        "slice_end": slice_end,
                        "candidate_name": candidate_name,
                        "candidate_description": candidate_description,
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

    def candidate_leaderboard(self) -> list[dict[str, object]]:
        rows = self.comparison_rows()
        candidate_names = sorted({str(row["candidate_name"]) for row in rows})
        leaderboard: list[dict[str, object]] = []
        for candidate_name in candidate_names:
            candidate_rows = [row for row in rows if str(row["candidate_name"]) == candidate_name]
            candidate_description = next(
                (
                    str(row["candidate_description"])
                    for row in candidate_rows
                    if row.get("candidate_description") is not None
                ),
                None,
            )
            avg_total_return_rank = self._average_rank(candidate_rows, "total_return")
            avg_capture_rank = self._average_rank(candidate_rows, "mainline_capture_ratio")
            avg_drawdown_rank = self._average_rank(candidate_rows, "max_drawdown")
            leaderboard.append(
                {
                    "candidate_name": candidate_name,
                    "candidate_description": candidate_description,
                    "row_count": len(candidate_rows),
                    "dataset_count": len({str(row["dataset_name"]) for row in candidate_rows}),
                    "slice_count": len(
                        {
                            (
                                str(row["dataset_name"]),
                                str(row["slice_name"]),
                            )
                            for row in candidate_rows
                        }
                    ),
                    "strategy_count": len({str(row["strategy_name"]) for row in candidate_rows}),
                    "mean_total_return": round(
                        sum(float(row["summary"]["total_return"]) for row in candidate_rows)
                        / len(candidate_rows),
                        6,
                    ),
                    "mean_mainline_capture_ratio": round(
                        sum(float(row["summary"]["mainline_capture_ratio"]) for row in candidate_rows)
                        / len(candidate_rows),
                        6,
                    ),
                    "mean_max_drawdown": round(
                        sum(float(row["summary"]["max_drawdown"]) for row in candidate_rows)
                        / len(candidate_rows),
                        6,
                    ),
                    "positive_total_return_rows": sum(
                        1 for row in candidate_rows if float(row["summary"]["total_return"]) > 0.0
                    ),
                    "avg_total_return_rank": avg_total_return_rank,
                    "avg_capture_rank": avg_capture_rank,
                    "avg_drawdown_rank": avg_drawdown_rank,
                    "composite_rank_score": round(
                        avg_total_return_rank + avg_capture_rank + avg_drawdown_rank,
                        6,
                    ),
                }
            )
        return sorted(
            leaderboard,
            key=lambda item: (
                float(item["composite_rank_score"]),
                float(item["avg_total_return_rank"]),
                float(item["avg_capture_rank"]),
            ),
        )

    def slice_summary(self) -> list[dict[str, object]]:
        rows = self.comparison_rows()
        grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
        for row in rows:
            key = (str(row["dataset_name"]), str(row["slice_name"]))
            grouped.setdefault(key, []).append(row)
        summaries: list[dict[str, object]] = []
        for (dataset_name, slice_name), group_rows in sorted(grouped.items()):
            best_total_return = max(group_rows, key=lambda item: float(item["summary"]["total_return"]))
            best_capture = max(
                group_rows,
                key=lambda item: float(item["summary"]["mainline_capture_ratio"]),
            )
            lowest_drawdown = min(group_rows, key=lambda item: float(item["summary"]["max_drawdown"]))
            summaries.append(
                {
                    "dataset_name": dataset_name,
                    "slice_name": slice_name,
                    "slice_start": best_total_return["slice_start"],
                    "slice_end": best_total_return["slice_end"],
                    "best_total_return": {
                        "candidate_name": best_total_return["candidate_name"],
                        "strategy_name": best_total_return["strategy_name"],
                    },
                    "best_capture": {
                        "candidate_name": best_capture["candidate_name"],
                        "strategy_name": best_capture["strategy_name"],
                    },
                    "lowest_drawdown": {
                        "candidate_name": lowest_drawdown["candidate_name"],
                        "strategy_name": lowest_drawdown["strategy_name"],
                    },
                }
            )
        return summaries

    def aggregate_summary(self) -> dict[str, object]:
        rows = self.comparison_rows()
        leaderboard = self.candidate_leaderboard()
        best_total_return = max(rows, key=lambda item: float(item["summary"]["total_return"]))
        best_capture = max(rows, key=lambda item: float(item["summary"]["mainline_capture_ratio"]))
        lowest_drawdown = min(rows, key=lambda item: float(item["summary"]["max_drawdown"]))
        return {
            "comparison_count": len(rows),
            "dataset_count": len({row["dataset_name"] for row in rows}),
            "slice_count": len({(row["dataset_name"], row["slice_name"]) for row in rows}),
            "candidate_count": len(leaderboard),
            "best_total_return": {
                "dataset_name": best_total_return["dataset_name"],
                "slice_name": best_total_return["slice_name"],
                "candidate_name": best_total_return["candidate_name"],
                "strategy_name": best_total_return["strategy_name"],
            },
            "best_capture": {
                "dataset_name": best_capture["dataset_name"],
                "slice_name": best_capture["slice_name"],
                "candidate_name": best_capture["candidate_name"],
                "strategy_name": best_capture["strategy_name"],
            },
            "lowest_drawdown": {
                "dataset_name": lowest_drawdown["dataset_name"],
                "slice_name": lowest_drawdown["slice_name"],
                "candidate_name": lowest_drawdown["candidate_name"],
                "strategy_name": lowest_drawdown["strategy_name"],
            },
            "most_stable_candidate": {
                "candidate_name": leaderboard[0]["candidate_name"],
                "composite_rank_score": leaderboard[0]["composite_rank_score"],
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

    def _average_rank(self, rows: list[dict[str, object]], metric_name: str) -> float:
        return round(
            sum(float(row["ranks"][metric_name]) for row in rows) / len(rows),
            6,
        )


class TimeSliceValidationRunner:
    """Run fixed configs across time slices for stronger validation analysis."""

    def __init__(self, *, engine: BacktestEngine) -> None:
        self.engine = engine

    def run(
        self,
        *,
        strategy_names: list[str],
        dataset_packs: list[DatasetPack],
        candidates: list[RuleCandidate],
        slices: list[ValidationSlice],
    ) -> TimeSliceValidationResult:
        suites: list[dict[str, object]] = []
        for dataset in dataset_packs:
            for validation_slice in slices:
                sliced_pack = self._slice_dataset_pack(dataset, validation_slice)
                for candidate in candidates:
                    merged_config = merge_config(dataset.config, candidate.override)
                    runner = StrategyExperimentRunner.from_config(
                        engine=self.engine,
                        config=merged_config,
                    )
                    suite = runner.run_suite(
                        strategy_names=strategy_names,
                        bars=sliced_pack.bars,
                        index_bars=sliced_pack.index_bars,
                        sector_snapshots=sliced_pack.sector_snapshots,
                        stock_snapshots=sliced_pack.stock_snapshots,
                        mainline_windows=sliced_pack.mainline_windows,
                    )
                    suites.append(
                        {
                            "dataset_name": dataset.dataset_name,
                            "slice_name": validation_slice.slice_name,
                            "slice_start": validation_slice.start_date.isoformat(),
                            "slice_end": validation_slice.end_date.isoformat(),
                            "candidate_name": candidate.candidate_name,
                            "candidate_description": candidate.description,
                            "suite": suite,
                        }
                    )
        return TimeSliceValidationResult(suites=suites)

    def _slice_dataset_pack(
        self,
        dataset: DatasetPack,
        validation_slice: ValidationSlice,
    ) -> DatasetPack:
        return DatasetPack(
            dataset_name=dataset.dataset_name,
            config=dataset.config,
            bars=self._filter_dated_records(dataset.bars, validation_slice),
            index_bars=self._filter_dated_records(dataset.index_bars or [], validation_slice),
            sector_snapshots=self._filter_dated_records(dataset.sector_snapshots, validation_slice),
            stock_snapshots=self._filter_dated_records(dataset.stock_snapshots, validation_slice),
            mainline_windows=self._filter_windows(dataset.mainline_windows, validation_slice),
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
