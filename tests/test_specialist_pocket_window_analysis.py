from __future__ import annotations

from a_share_quant.strategy.specialist_pocket_window_analysis import SpecialistPocketWindowAnalyzer


def test_specialist_pocket_window_analyzer_finds_windows_missed_by_both_anchors() -> None:
    payload = {
        "comparisons": [
            {
                "dataset_name": "theme_research_v4",
                "slice_name": "2024_q1",
                "strategy_name": "mainline_trend_c",
                "candidate_name": "shared_default",
                "window_breakdown": [
                    {
                        "window_id": "AAA_1",
                        "symbol": "AAA",
                        "capturable_return": 0.05,
                        "capture_ratio": 0.10,
                        "missed": False,
                    },
                    {
                        "window_id": "BBB_1",
                        "symbol": "BBB",
                        "capturable_return": 0.04,
                        "capture_ratio": 0.00,
                        "missed": True,
                    },
                ],
            },
            {
                "dataset_name": "theme_research_v4",
                "slice_name": "2024_q1",
                "strategy_name": "mainline_trend_c",
                "candidate_name": "buffer_only_012",
                "window_breakdown": [
                    {
                        "window_id": "AAA_1",
                        "symbol": "AAA",
                        "capturable_return": 0.05,
                        "capture_ratio": 0.20,
                        "missed": False,
                    },
                    {
                        "window_id": "BBB_1",
                        "symbol": "BBB",
                        "capturable_return": 0.04,
                        "capture_ratio": 0.00,
                        "missed": True,
                    },
                ],
            },
            {
                "dataset_name": "theme_research_v4",
                "slice_name": "2024_q1",
                "strategy_name": "mainline_trend_c",
                "candidate_name": "baseline_expansion_branch",
                "window_breakdown": [
                    {
                        "window_id": "AAA_1",
                        "symbol": "AAA",
                        "capturable_return": 0.05,
                        "capture_ratio": 0.35,
                        "missed": False,
                    },
                    {
                        "window_id": "BBB_1",
                        "symbol": "BBB",
                        "capturable_return": 0.04,
                        "capture_ratio": 0.45,
                        "missed": False,
                    },
                ],
            },
        ]
    }

    result = SpecialistPocketWindowAnalyzer().analyze(
        payload=payload,
        dataset_name="theme_research_v4",
        slice_name="2024_q1",
        strategy_name="mainline_trend_c",
        specialist_candidate="baseline_expansion_branch",
        anchor_candidates=["shared_default", "buffer_only_012"],
    )

    assert result.summary["improved_window_count"] == 2
    assert result.summary["both_anchors_missed_window_count"] == 1
    assert result.summary["top_symbol"] == "BBB"
    assert result.top_window_edges[0]["window_id"] == "BBB_1"
