from __future__ import annotations

from a_share_quant.strategy.environment_boundary import EnvironmentBoundaryAnalyzer


def test_environment_boundary_analyzer_summarizes_stability_and_specialists() -> None:
    payload = {
        "source_report": "dummy.json",
        "extras": {
            "candidate_leaderboard": [
                {
                    "candidate_name": "balanced_compromise",
                    "composite_rank_score": 10.0,
                    "mean_total_return": 0.01,
                    "mean_mainline_capture_ratio": 0.20,
                    "mean_max_drawdown": 0.01,
                    "positive_total_return_rows": 6,
                },
                {
                    "candidate_name": "baseline_expansion_branch",
                    "composite_rank_score": 12.0,
                    "mean_total_return": 0.009,
                    "mean_mainline_capture_ratio": 0.24,
                    "mean_max_drawdown": 0.013,
                    "positive_total_return_rows": 5,
                },
                {
                    "candidate_name": "theme_strict_quality_branch",
                    "composite_rank_score": 13.0,
                    "mean_total_return": 0.006,
                    "mean_mainline_capture_ratio": 0.17,
                    "mean_max_drawdown": 0.008,
                    "positive_total_return_rows": 4,
                },
            ],
            "slice_summary": [
                {
                    "dataset_name": "baseline",
                    "slice_name": "q1",
                    "best_total_return": {"candidate_name": "balanced_compromise", "strategy_name": "a"},
                    "best_capture": {"candidate_name": "baseline_expansion_branch", "strategy_name": "b"},
                    "lowest_drawdown": {"candidate_name": "theme_strict_quality_branch", "strategy_name": "a"},
                },
                {
                    "dataset_name": "theme",
                    "slice_name": "q2",
                    "best_total_return": {"candidate_name": "theme_strict_quality_branch", "strategy_name": "c"},
                    "best_capture": {"candidate_name": "baseline_expansion_branch", "strategy_name": "c"},
                    "lowest_drawdown": {"candidate_name": "theme_strict_quality_branch", "strategy_name": "a"},
                },
            ],
        },
    }

    result = EnvironmentBoundaryAnalyzer().analyze(payload)

    assert result.boundary_summary["most_stable_candidate"]["candidate_name"] == "balanced_compromise"
    assert result.boundary_summary["capture_specialist"]["candidate_name"] == "baseline_expansion_branch"
    assert result.boundary_summary["drawdown_specialist"]["candidate_name"] == "theme_strict_quality_branch"
    assert len(result.candidate_overview) == 3
