from __future__ import annotations

from a_share_quant.strategy.specialist_alpha_analysis import SpecialistAlphaAnalyzer


def test_specialist_alpha_analyzer_finds_capture_specialist_pocket() -> None:
    payload = {
        "comparisons": [
            {
                "dataset_name": "baseline_research_v1",
                "slice_name": "2024_q1",
                "strategy_name": "mainline_trend_b",
                "candidate_name": "shared_default",
                "summary": {
                    "total_return": 0.01,
                    "mainline_capture_ratio": 0.20,
                    "max_drawdown": 0.01,
                },
            },
            {
                "dataset_name": "baseline_research_v1",
                "slice_name": "2024_q1",
                "strategy_name": "mainline_trend_b",
                "candidate_name": "buffer_only_012",
                "summary": {
                    "total_return": 0.012,
                    "mainline_capture_ratio": 0.22,
                    "max_drawdown": 0.009,
                },
            },
            {
                "dataset_name": "baseline_research_v1",
                "slice_name": "2024_q1",
                "strategy_name": "mainline_trend_b",
                "candidate_name": "baseline_expansion_branch",
                "summary": {
                    "total_return": 0.013,
                    "mainline_capture_ratio": 0.27,
                    "max_drawdown": 0.011,
                },
            },
            {
                "dataset_name": "baseline_research_v1",
                "slice_name": "2024_q1",
                "strategy_name": "mainline_trend_b",
                "candidate_name": "theme_strict_quality_branch",
                "summary": {
                    "total_return": 0.009,
                    "mainline_capture_ratio": 0.18,
                    "max_drawdown": 0.008,
                },
            },
        ]
    }

    result = SpecialistAlphaAnalyzer().analyze(
        payload=payload,
        anchors=["shared_default", "buffer_only_012"],
        specialists=[
            {
                "candidate_name": "baseline_expansion_branch",
                "primary_metric": "mainline_capture_ratio",
                "min_primary_advantage": 0.01,
                "max_secondary_penalty": 0.003,
            }
        ],
    )

    assert result.summary["top_specialist_by_opportunity_count"] == "baseline_expansion_branch"
    assert result.specialist_summaries[0]["opportunity_count"] == 1
