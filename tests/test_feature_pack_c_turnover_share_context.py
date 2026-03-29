from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.feature_pack_c_turnover_share_context import (
    FeaturePackCTurnoverShareContextAnalyzer,
)


def _write_stock_snapshots_csv(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "trade_date,symbol,sector_id,sector_name,expected_upside,drive_strength,stability,liquidity,late_mover_quality,resonance,concept_support,primary_concept_weight,concept_count,concept_concentration_ratio,leader_component_score,core_component_score,late_component_score,non_junk_composite_score,late_quality_raw_score,late_quality_concept_boost,late_quality_sector_strength,late_quality_lag_balance,late_quality_trend_support,stability_volatility,liquidity_turnover_share,liquidity_turnover_rank,liquidity_sector_turnover_share,liquidity_sector_top_turnover_share,liquidity_sector_mean_turnover_share,liquidity_sector_turnover_share_gap,late_quality_sector_contribution,late_quality_stability_contribution,late_quality_liquidity_contribution,late_quality_lag_contribution,late_quality_trend_contribution",
                "2024-10-23,002902,S1,Sector 1,0.6,0.7,0.28,0.25,0.615669,0.67,0.0,0.0,0,0.0,0.75,0.40,0.66,0.75,0.615669,0.0,0.734287,0.888889,1.0,0.043,0.021,0.254,0.18,0.44,0.25,0.26,0.220286,0.111122,0.050927,0.133333,0.1",
                "2024-11-28,002902,S1,Sector 1,0.6,0.7,0.28,0.25,0.589676,0.67,0.0,0.0,0,0.0,0.75,0.40,0.66,0.75,0.589676,0.0,0.677855,0.888889,0.274986,0.034,0.051,0.622,0.31,0.35,0.25,0.04,0.203357,0.182048,0.124488,0.133333,0.027499",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_feature_pack_c_turnover_share_context_classifies_peer_vs_broad_attention(tmp_path: Path) -> None:
    stock_snapshots_csv = tmp_path / "stock_snapshots.csv"
    _write_stock_snapshots_csv(stock_snapshots_csv)
    context_payload = {
        "case_rows": [
            {
                "case_name": "theme_q4_002902_b",
                "trigger_date": "2024-10-23",
                "symbol": "002902",
                "mechanism_type": "other_worse_loss_shift",
                "local_context_class": "turnover_share_led",
            },
            {
                "case_name": "theme_q4_002902_b",
                "trigger_date": "2024-11-28",
                "symbol": "002902",
                "mechanism_type": "entry_suppression_avoidance",
                "local_context_class": "turnover_share_led",
            },
        ]
    }

    result = FeaturePackCTurnoverShareContextAnalyzer().analyze(
        context_payload=context_payload,
        stock_snapshots_csv=stock_snapshots_csv,
        case_names=["theme_q4_002902_b"],
    )

    assert result.summary["row_count"] == 2
    assert result.summary["local_turnover_context_counts"]["sector_peer_dominance"] == 1
    assert result.summary["local_turnover_context_counts"]["balanced_share_weakness"] == 1
    assert result.summary["recommended_fourth_feature_group"] in {
        "late_quality_sector_peer_attention_context",
        "late_quality_broad_attention_context",
        "late_quality_balanced_turnover_context",
    }
