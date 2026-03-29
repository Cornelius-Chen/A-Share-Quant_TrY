from __future__ import annotations

from a_share_quant.strategy.permission_loss_edge_analysis import PermissionLossEdgeAnalyzer


def test_permission_loss_edge_analyzer_highlights_threshold_edge_and_buy_suppression() -> None:
    result = PermissionLossEdgeAnalyzer().analyze(
        symbol="300750",
        trade_date="2024-02-05",
        ranked_sector_scores=[
            {
                "sector_id": "BK1173",
                "sector_name": "theme",
                "rank": 1,
                "composite_score": 2.583525,
            },
            {
                "sector_id": "BK0895",
                "sector_name": "secondary",
                "rank": 2,
                "composite_score": 2.551,
            },
        ],
        candidate_evaluations=[
            {
                "candidate_name": "shared_default",
                "role": "incumbent",
                "permission_allowed": True,
                "permission_reason": "approved",
            },
            {
                "candidate_name": "buffer_only_012",
                "role": "challenger",
                "permission_allowed": False,
                "permission_reason": "top_score_below_threshold",
            },
        ],
        action_rows=[
            {
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_a",
                "emitted_actions": ["buy"],
            },
            {
                "candidate_name": "buffer_only_012",
                "strategy_name": "mainline_trend_a",
                "emitted_actions": [],
            },
        ],
    )

    assert result.summary["symbol"] == "300750"
    assert result.summary["top_sector"]["sector_id"] == "BK1173"
    assert len(result.candidate_evaluations) == 2
    assert result.candidate_evaluations[0]["permission_allowed"] is True
    assert result.candidate_evaluations[1]["permission_allowed"] is False
