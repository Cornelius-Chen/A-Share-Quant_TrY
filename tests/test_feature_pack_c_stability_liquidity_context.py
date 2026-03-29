from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.feature_pack_c_stability_liquidity_context import (
    FeaturePackCStabilityLiquidityContextAnalyzer,
)


def _write_stock_snapshots_csv(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "trade_date,symbol,sector_id,sector_name,expected_upside,drive_strength,stability,liquidity,late_mover_quality,resonance,concept_support,primary_concept_weight,concept_count,concept_concentration_ratio,leader_component_score,core_component_score,late_component_score,non_junk_composite_score,late_quality_raw_score,late_quality_concept_boost,late_quality_sector_strength,late_quality_lag_balance,late_quality_trend_support,stability_volatility,liquidity_turnover_share,liquidity_turnover_rank,late_quality_sector_contribution,late_quality_stability_contribution,late_quality_liquidity_contribution,late_quality_lag_contribution,late_quality_trend_contribution",
                "2024-10-31,002902,S1,Sector 1,0.6,0.7,0.28,0.25,0.575792,0.67,0.0,0.0,0,0.0,0.75,0.40,0.66,0.75,0.575792,0.0,0.779385,0.888889,0.874504,0.048018,0.083333,0.252174,0.233815,0.070759,0.050435,0.133333,0.08745",
                "2024-05-09,002466,S2,Sector 2,0.59,0.58,0.62,0.52,0.623358,0.69,0.518548,0.526497,2,0.526497,0.58,0.50,0.61,0.61,0.581874,0.041484,0.893125,0.555556,0.428718,0.037404,0.122276,0.183416,0.267938,0.155849,0.073366,0.083333,0.042872",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_feature_pack_c_stability_liquidity_context_classifies_local_contexts(tmp_path: Path) -> None:
    stock_snapshots_csv = tmp_path / "stock_snapshots.csv"
    _write_stock_snapshots_csv(stock_snapshots_csv)
    residual_payload = {
        "case_rows": [
            {
                "case_name": "theme_q4_002902_b",
                "trigger_date": "2024-10-31",
                "symbol": "002902",
                "mechanism_type": "earlier_exit_loss_reduction",
                "dominant_residual_component": "stability",
            },
            {
                "case_name": "theme_q2_002466_c",
                "trigger_date": "2024-05-09",
                "symbol": "002466",
                "mechanism_type": "entry_suppression_avoidance",
                "dominant_residual_component": "liquidity",
            },
        ]
    }

    result = FeaturePackCStabilityLiquidityContextAnalyzer().analyze(
        residual_payload=residual_payload,
        stock_snapshots_csv=stock_snapshots_csv,
        case_names=["theme_q4_002902_b", "theme_q2_002466_c"],
    )

    assert result.summary["row_count"] == 2
    assert result.summary["local_context_counts"]["volatility_led"] == 1
    assert result.summary["local_context_counts"]["turnover_share_led"] == 1
    assert result.summary["recommended_third_feature_group"] in {
        "late_quality_volatility_context",
        "late_quality_turnover_share_context",
        "late_quality_turnover_rank_context",
        "late_quality_mixed_stability_liquidity_context",
    }
