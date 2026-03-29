from __future__ import annotations

from dataclasses import dataclass

from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.common.config import merge_config
from a_share_quant.strategy.dataset_comparison import DatasetPack
from a_share_quant.strategy.experiment_runner import StrategyExperimentRunner, StrategySuiteResult


@dataclass(slots=True)
class RuleCandidate:
    candidate_name: str
    override: dict[str, object]
    description: str | None = None


@dataclass(slots=True)
class RuleSweepResult:
    suites: list[dict[str, object]]

    def comparison_rows(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for suite_entry in self.suites:
            suite = suite_entry["suite"]
            assert isinstance(suite, StrategySuiteResult)
            dataset_name = str(suite_entry["dataset_name"])
            candidate_name = str(suite_entry["candidate_name"])
            candidate_description = suite_entry.get("candidate_description")
            for row in suite.comparison_rows():
                rows.append(
                    {
                        "dataset_name": dataset_name,
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
            candidate_rows = [
                row
                for row in rows
                if str(row["candidate_name"]) == candidate_name
            ]
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
            composite_rank_score = round(
                avg_total_return_rank + avg_capture_rank + avg_drawdown_rank,
                6,
            )
            leaderboard.append(
                {
                    "candidate_name": candidate_name,
                    "candidate_description": candidate_description,
                    "row_count": len(candidate_rows),
                    "dataset_count": len({str(row["dataset_name"]) for row in candidate_rows}),
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
                    "avg_total_return_rank": avg_total_return_rank,
                    "avg_capture_rank": avg_capture_rank,
                    "avg_drawdown_rank": avg_drawdown_rank,
                    "composite_rank_score": composite_rank_score,
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

    def aggregate_summary(self) -> dict[str, object]:
        rows = self.comparison_rows()
        leaderboard = self.candidate_leaderboard()
        best_total_return = max(rows, key=lambda item: float(item["summary"]["total_return"]))
        best_capture = max(rows, key=lambda item: float(item["summary"]["mainline_capture_ratio"]))
        lowest_drawdown = min(rows, key=lambda item: float(item["summary"]["max_drawdown"]))
        most_stable_candidate = leaderboard[0]
        return {
            "comparison_count": len(rows),
            "dataset_count": len({row["dataset_name"] for row in rows}),
            "candidate_count": len(leaderboard),
            "best_total_return": {
                "dataset_name": best_total_return["dataset_name"],
                "candidate_name": best_total_return["candidate_name"],
                "strategy_name": best_total_return["strategy_name"],
            },
            "best_capture": {
                "dataset_name": best_capture["dataset_name"],
                "candidate_name": best_capture["candidate_name"],
                "strategy_name": best_capture["strategy_name"],
            },
            "lowest_drawdown": {
                "dataset_name": lowest_drawdown["dataset_name"],
                "candidate_name": lowest_drawdown["candidate_name"],
                "strategy_name": lowest_drawdown["strategy_name"],
            },
            "most_stable_candidate": {
                "candidate_name": most_stable_candidate["candidate_name"],
                "composite_rank_score": most_stable_candidate["composite_rank_score"],
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

    def _average_rank(
        self,
        rows: list[dict[str, object]],
        metric_name: str,
    ) -> float:
        return round(
            sum(float(row["ranks"][metric_name]) for row in rows) / len(rows),
            6,
        )


class RuleSweepRunner:
    """Compare named rule candidates across multiple dataset packs."""

    def __init__(self, *, engine: BacktestEngine) -> None:
        self.engine = engine

    def run(
        self,
        *,
        strategy_names: list[str],
        dataset_packs: list[DatasetPack],
        candidates: list[RuleCandidate],
    ) -> RuleSweepResult:
        suites: list[dict[str, object]] = []
        for dataset in dataset_packs:
            for candidate in candidates:
                merged_config = merge_config(dataset.config, candidate.override)
                runner = StrategyExperimentRunner.from_config(
                    engine=self.engine,
                    config=merged_config,
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
                        "candidate_name": candidate.candidate_name,
                        "candidate_description": candidate.description,
                        "suite": suite,
                    }
                )
        return RuleSweepResult(suites=suites)
