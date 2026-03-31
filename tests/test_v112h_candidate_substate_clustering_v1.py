from __future__ import annotations

from a_share_quant.strategy.v112b_baseline_readout_v1 import TrainingSample
from a_share_quant.strategy.v112h_candidate_substate_clustering_v1 import V112HCandidateSubstateClusteringAnalyzer


def _sample(
    trade_date: str,
    symbol: str,
    label: str,
    breadth: float,
    freshness: float,
    persistence: float,
) -> TrainingSample:
    feature_values = {
        "product_price_change_proxy": persistence,
        "demand_acceleration_proxy": freshness,
        "supply_tightness_proxy": 0.1,
        "official_or_industry_catalyst_presence": 0.5,
        "revenue_sensitivity_class": 0.8,
        "gross_margin_sensitivity_class": 0.7,
        "order_or_capacity_sensitivity_proxy": 0.3,
        "earnings_revision_pressure_proxy": 0.2,
        "rerating_gap_proxy": 0.1,
        "relative_strength_persistence": persistence,
        "volume_expansion_confirmation": 1.0,
        "breakout_or_hold_structure": 1.0 if breadth >= 0.5 else 0.0,
        "catalyst_freshness_state": freshness,
        "cross_day_catalyst_persistence": persistence,
        "theme_breadth_confirmation_proxy": breadth,
    }
    return TrainingSample(
        trade_date=trade_date,
        symbol=symbol,
        stage="high_level_consolidation",
        label=label,
        feature_values=feature_values,
        forward_return_20d=0.0,
        max_drawdown_20d=0.0,
        forward_return_bucket="flat",
        max_drawdown_bucket="flat",
    )


def test_v112h_candidate_substate_clustering_groups_four_candidate_substates() -> None:
    analyzer = V112HCandidateSubstateClusteringAnalyzer()
    samples = [
        _sample("2026-01-01", "300502", "failed", 0.8, 0.2, 0.2),
        _sample("2026-01-02", "300502", "carry_constructive", 0.8, 0.15, 0.18),
        _sample("2026-01-03", "300502", "failed", 0.8, 0.0, 0.0),
        _sample("2026-01-04", "300502", "failed", 0.2, 0.2, 0.18),
        _sample("2026-01-05", "300502", "watch_constructive", 0.2, 0.0, 0.0),
        _sample("2026-01-06", "300502", "failed", 0.2, 0.0, 0.18),
    ]

    result = analyzer._build_from_samples(  # noqa: SLF001
        samples=samples,
        baseline_summary={"test_accuracy": 0.5},
        gbdt_summary={"gbdt_v2_test_accuracy": 0.6},
    )

    assert result.summary["candidate_cluster_count"] == 4
    assert len(result.cluster_rows) == 4
    assert any(row["support_level"] == "thin" for row in result.cluster_rows)
