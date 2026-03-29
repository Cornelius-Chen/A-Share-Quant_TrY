from __future__ import annotations

from datetime import date
from pathlib import Path

from a_share_quant.common.models import StockSnapshot
from a_share_quant.strategy.feature_pack_c_late_quality_residuals import (
    FeaturePackCLateQualityResidualsAnalyzer,
)


def _write_stock_snapshots_csv(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "trade_date,symbol,sector_id,sector_name,expected_upside,drive_strength,stability,liquidity,late_mover_quality,resonance,concept_support,primary_concept_weight,concept_count,concept_concentration_ratio,leader_component_score,core_component_score,late_component_score,non_junk_composite_score,late_quality_raw_score,late_quality_concept_boost,late_quality_sector_strength,late_quality_lag_balance,late_quality_trend_support,late_quality_sector_contribution,late_quality_stability_contribution,late_quality_liquidity_contribution,late_quality_lag_contribution,late_quality_trend_contribution",
                "2024-10-31,002902,S1,Sector 1,0.6,0.7,0.5,0.6,0.575792,0.67,0.0,0.0,0,0.0,0.75,0.40,0.66,0.75,0.575792,0.0,0.52,0.30,0.20,0.156,0.125,0.120,0.045,0.020",
                "2024-04-08,002466,S2,Sector 2,0.59,0.58,0.52,0.55,0.542706,0.58,0.574228,0.60604,2,0.60604,0.58,0.50,0.59,0.59,0.496768,0.045938,0.41,0.18,0.10,0.123,0.130,0.110,0.027,0.010",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_feature_pack_c_late_quality_residuals_finds_dominant_components(tmp_path: Path) -> None:
    stock_snapshots_csv = tmp_path / "stock_snapshots.csv"
    _write_stock_snapshots_csv(stock_snapshots_csv)
    recheck_payload = {
        "case_rows": [
            {
                "case_name": "theme_q4_002902_b",
                "trigger_date": "2024-10-31",
                "symbol": "002902",
                "mechanism_type": "earlier_exit_loss_reduction",
                "challenger_assignment_reason": "highest_leader_score",
                "challenger_late_quality_margin": -0.074208,
            },
            {
                "case_name": "theme_q2_002466_c",
                "trigger_date": "2024-04-08",
                "symbol": "002466",
                "mechanism_type": "preemptive_loss_avoidance_shift",
                "challenger_assignment_reason": "low_composite_or_low_resonance",
                "challenger_late_quality_margin": -0.107294,
            },
        ]
    }

    result = FeaturePackCLateQualityResidualsAnalyzer().analyze(
        recheck_payload=recheck_payload,
        stock_snapshots_csv=stock_snapshots_csv,
        case_names=["theme_q4_002902_b", "theme_q2_002466_c"],
    )

    assert result.summary["row_count"] == 2
    assert result.summary["concept_boost_active_count"] == 1
    assert result.summary["raw_below_threshold_count"] == 2
    assert result.summary["recommended_second_feature_group"] in {
        "late_quality_sector_strength_context",
        "late_quality_stability_context",
        "late_quality_liquidity_context",
        "late_quality_stability_liquidity_context",
        "late_quality_lag_balance_context",
        "late_quality_trend_support_context",
    }
    assert result.case_rows[0]["dominant_residual_component"] in {
        "sector_strength",
        "lag_balance",
        "trend_support",
        "stability",
        "liquidity",
    }
    assert any(row["late_quality_concept_boost"] > 0.0 for row in result.case_rows)
