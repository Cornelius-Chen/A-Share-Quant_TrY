from __future__ import annotations

from a_share_quant.strategy.v112b_baseline_readout_v1 import TrainingSample
from a_share_quant.strategy.v112h_hotspot_bucketization_v1 import V112HHotspotBucketizationAnalyzer


def _sample(
    *,
    trade_date: str,
    symbol: str,
    stage: str,
    label: str,
    breadth: float,
    freshness: float,
    persistence: float,
    baseline_correct: bool,
    gbdt_correct: bool,
) -> dict[str, object]:
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
    return {
        "sample": TrainingSample(
            trade_date=trade_date,
            symbol=symbol,
            stage=stage,
            label=label,
            feature_values=feature_values,
            forward_return_20d=0.0,
            max_drawdown_20d=0.0,
            forward_return_bucket="flat",
            max_drawdown_bucket="flat",
        ),
        "baseline_correct": baseline_correct,
        "gbdt_correct": gbdt_correct,
    }


def test_v112h_hotspot_bucketization_groups_misreads_into_reviewable_buckets() -> None:
    analyzer = V112HHotspotBucketizationAnalyzer()
    records = [
        _sample(
            trade_date="2026-01-01",
            symbol="300308",
            stage="high_level_consolidation",
            label="failed",
            breadth=0.8,
            freshness=0.2,
            persistence=0.2,
            baseline_correct=False,
            gbdt_correct=True,
        ),
        _sample(
            trade_date="2026-01-02",
            symbol="300308",
            stage="high_level_consolidation",
            label="carry_constructive",
            breadth=0.8,
            freshness=0.15,
            persistence=0.18,
            baseline_correct=False,
            gbdt_correct=False,
        ),
        _sample(
            trade_date="2026-01-03",
            symbol="300502",
            stage="major_markup",
            label="failed",
            breadth=0.2,
            freshness=0.0,
            persistence=0.18,
            baseline_correct=False,
            gbdt_correct=True,
        ),
        _sample(
            trade_date="2026-01-04",
            symbol="300502",
            stage="major_markup",
            label="carry_constructive",
            breadth=0.2,
            freshness=0.0,
            persistence=0.0,
            baseline_correct=True,
            gbdt_correct=False,
        ),
    ]

    bucket_groups = {}
    for item in records:
        row = item["sample"]
        record = {
            "trade_date": row.trade_date,
            "symbol": row.symbol,
            "stage": row.stage,
            "true_label": row.label,
            "baseline_predicted_label": "carry_constructive" if not item["baseline_correct"] else row.label,
            "baseline_correct": item["baseline_correct"],
            "gbdt_predicted_label": "carry_constructive" if not item["gbdt_correct"] else row.label,
            "gbdt_correct": item["gbdt_correct"],
            "feature_values": row.feature_values,
        }
        bucket_name = analyzer._bucket_name(record)  # noqa: SLF001
        bucket_groups.setdefault(bucket_name, []).append(record)

    assert len(bucket_groups) == 3
    bucket_rows = [analyzer._build_bucket_row(bucket_name=name, rows=rows) for name, rows in bucket_groups.items()]  # noqa: SLF001
    assert all(row["sample_count"] >= 1 for row in bucket_rows)
    assert any("high_level_consolidation" in row["bucket_name"] for row in bucket_rows)
    assert any("major_markup" in row["bucket_name"] for row in bucket_rows)
