from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.feature_pack_c_balanced_turnover_weakness import (
    FeaturePackCBalancedTurnoverWeaknessAnalyzer,
)


def _write_stock_snapshots_csv(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "trade_date,symbol,sector_id,sector_name,expected_upside,drive_strength,stability,liquidity,late_mover_quality,resonance,concept_support,primary_concept_weight,concept_count,concept_concentration_ratio,leader_component_score,core_component_score,late_component_score,non_junk_composite_score,late_quality_raw_score,late_quality_concept_boost,late_quality_sector_strength,late_quality_lag_balance,late_quality_trend_support,stability_volatility,liquidity_turnover_share,liquidity_turnover_rank,liquidity_sector_turnover_share,liquidity_sector_top_turnover_share,liquidity_sector_mean_turnover_share,liquidity_sector_turnover_share_gap,liquidity_sector_symbol_count,late_quality_sector_contribution,late_quality_stability_contribution,late_quality_liquidity_contribution,late_quality_lag_contribution,late_quality_trend_contribution",
                "2024-10-23,002902,S1,Sector 1,0.6,0.7,0.28,0.25,0.615669,0.67,0.0,0.0,0,0.0,0.75,0.40,0.66,0.75,0.615669,0.0,0.734287,0.888889,1.0,0.043,0.091061,0.5,1.0,1.0,1.0,0.0,1,0.220286,0.111122,0.050927,0.133333,0.1",
                "2024-05-09,002466,S2,Sector 2,0.59,0.58,0.62,0.52,0.623358,0.69,0.518548,0.526497,2,0.526497,0.58,0.50,0.61,0.61,0.623358,0.0,0.893125,0.555556,0.428721,0.022596,0.111384,0.75,0.130391,0.4076,0.111111,0.277209,4,0.267938,0.155849,0.073366,0.083333,0.042872",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_feature_pack_c_balanced_turnover_weakness_detects_singleton_sector_masking(tmp_path: Path) -> None:
    stock_snapshots_csv = tmp_path / "stock_snapshots.csv"
    _write_stock_snapshots_csv(stock_snapshots_csv)
    turnover_context_payload = {
        "case_rows": [
            {
                "case_name": "theme_q4_002902_b",
                "trigger_date": "2024-10-23",
                "symbol": "002902",
                "mechanism_type": "other_worse_loss_shift",
                "local_turnover_context": "balanced_share_weakness",
            },
            {
                "case_name": "theme_q2_002466_c",
                "trigger_date": "2024-05-09",
                "symbol": "002466",
                "mechanism_type": "entry_suppression_avoidance",
                "local_turnover_context": "balanced_share_weakness",
            },
        ]
    }

    result = FeaturePackCBalancedTurnoverWeaknessAnalyzer().analyze(
        turnover_context_payload=turnover_context_payload,
        stock_snapshots_csv=stock_snapshots_csv,
        case_names=["theme_q4_002902_b", "theme_q2_002466_c"],
    )

    assert result.summary["row_count"] == 2
    assert result.summary["balanced_weakness_counts"]["singleton_sector_masking"] == 1
    assert result.summary["balanced_weakness_counts"]["true_balanced_share_weakness"] == 1
