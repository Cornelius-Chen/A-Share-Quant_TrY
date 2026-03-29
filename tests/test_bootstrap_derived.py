from __future__ import annotations

from datetime import date
from pathlib import Path

from a_share_quant.common.models import DailyBar
from a_share_quant.data.bootstrap_derived import BootstrapDerivedConfig, BootstrapDerivedDataBuilder
from a_share_quant.trend.leader_hierarchy_ranker import HierarchyConfig, LeaderHierarchyRanker


def build_bar(
    trade_date: str,
    symbol: str,
    close_price: float,
    *,
    pre_close: float,
    turnover: float = 100_000_000,
) -> DailyBar:
    return DailyBar(
        trade_date=date.fromisoformat(trade_date),
        symbol=symbol,
        open=close_price,
        high=close_price * 1.01,
        low=close_price * 0.99,
        close=close_price,
        volume=1_000_000,
        turnover=turnover,
        pre_close=pre_close,
        adjust_factor=1.0,
        listed_days=300,
    )


def test_bootstrap_derived_builder_outputs_tables(tmp_path: Path) -> None:
    bars = [
        build_bar("2025-01-02", "AAA", 10.0, pre_close=9.8),
        build_bar("2025-01-03", "AAA", 10.5, pre_close=10.0),
        build_bar("2025-01-06", "AAA", 10.8, pre_close=10.5),
        build_bar("2025-01-02", "BBB", 20.0, pre_close=20.1),
        build_bar("2025-01-03", "BBB", 19.8, pre_close=20.0),
        build_bar("2025-01-06", "BBB", 20.2, pre_close=19.8),
    ]
    config = BootstrapDerivedConfig(
        bars_csv=tmp_path / "bars.csv",
        mapping_input_csv=None,
        concept_mapping_input_csv=None,
        mapping_output_csv=tmp_path / "sector_mapping.csv",
        sector_snapshots_output_csv=tmp_path / "sector_snapshots.csv",
        stock_snapshots_output_csv=tmp_path / "stock_snapshots.csv",
        mainline_windows_output_csv=tmp_path / "mainline_windows.csv",
        mapping_source="test",
        mapping_version="test_v1",
        protocol_version="protocol_v1.0",
        sector_assignments={
            "AAA": {"sector_id": "ALPHA", "sector_name": "Alpha"},
            "BBB": {"sector_id": "BETA", "sector_name": "Beta"},
        },
        lookback=3,
        top_sector_score_threshold=0.3,
        top_sector_rank_limit=1,
        min_window_length=1,
    )

    outputs = BootstrapDerivedDataBuilder(config).build(bars)

    assert outputs["sector_mapping_daily"].exists()
    assert outputs["sector_snapshots"].exists()
    assert outputs["stock_snapshots"].exists()
    assert outputs["mainline_windows"].exists()
    assert outputs["sector_snapshots"].read_text(encoding="utf-8").count("\n") >= 2
    assert outputs["stock_snapshots"].read_text(encoding="utf-8").count("\n") >= 2


def test_bootstrap_derived_supports_late_mover_classification(tmp_path: Path) -> None:
    bars = [
        build_bar("2025-01-02", "AAA", 10.0, pre_close=9.8, turnover=220_000_000),
        build_bar("2025-01-03", "AAA", 10.8, pre_close=10.0, turnover=240_000_000),
        build_bar("2025-01-06", "AAA", 11.5, pre_close=10.8, turnover=260_000_000),
        build_bar("2025-01-02", "BBB", 10.0, pre_close=9.9, turnover=300_000_000),
        build_bar("2025-01-03", "BBB", 10.3, pre_close=10.0, turnover=320_000_000),
        build_bar("2025-01-06", "BBB", 10.6, pre_close=10.3, turnover=340_000_000),
        build_bar("2025-01-02", "CCC", 10.0, pre_close=10.0, turnover=180_000_000),
        build_bar("2025-01-03", "CCC", 10.2, pre_close=10.0, turnover=200_000_000),
        build_bar("2025-01-06", "CCC", 10.9, pre_close=10.2, turnover=230_000_000),
    ]
    config = BootstrapDerivedConfig(
        bars_csv=tmp_path / "bars.csv",
        mapping_input_csv=None,
        concept_mapping_input_csv=None,
        mapping_output_csv=tmp_path / "sector_mapping.csv",
        sector_snapshots_output_csv=tmp_path / "sector_snapshots.csv",
        stock_snapshots_output_csv=tmp_path / "stock_snapshots.csv",
        mainline_windows_output_csv=tmp_path / "mainline_windows.csv",
        mapping_source="test",
        mapping_version="test_v1",
        protocol_version="protocol_v1.0",
        sector_assignments={
            "AAA": {"sector_id": "ALPHA", "sector_name": "Alpha"},
            "BBB": {"sector_id": "ALPHA", "sector_name": "Alpha"},
            "CCC": {"sector_id": "ALPHA", "sector_name": "Alpha"},
        },
        lookback=3,
        top_sector_score_threshold=0.3,
        top_sector_rank_limit=1,
        min_window_length=1,
    )

    builder = BootstrapDerivedDataBuilder(config)
    mappings = builder._build_sector_mappings(bars)
    sector_snapshots = builder._build_sector_snapshots(bars, mappings)
    stock_snapshots = builder._build_stock_snapshots(bars, mappings, sector_snapshots)
    latest_snapshots = [item for item in stock_snapshots if item.trade_date == date(2025, 1, 6)]

    assignments = LeaderHierarchyRanker(
        HierarchyConfig(
            min_resonance_for_core=0.55,
            min_quality_for_late_mover=0.55,
            min_composite_for_non_junk=0.55,
        )
    ).rank(latest_snapshots)
    layers = {item.symbol: item.layer for item in assignments}

    assert layers["AAA"] == "leader"
    assert layers["BBB"] == "core"
    assert layers["CCC"] == "late_mover"


def test_bootstrap_derived_prefers_primary_concept_mapping_when_available(tmp_path: Path) -> None:
    bars = [
        build_bar("2025-01-02", "AAA", 10.0, pre_close=9.8),
        build_bar("2025-01-02", "BBB", 20.0, pre_close=19.8),
    ]
    mapping_input = tmp_path / "sector_mapping.csv"
    mapping_input.write_text(
        "\n".join(
            [
                "trade_date,symbol,sector_id,sector_name,mapping_source,mapping_version",
                "2025-01-02,AAA,FINANCE,Finance,cninfo,v1",
                "2025-01-02,BBB,CONSUMER,Consumer,cninfo,v1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    concept_input = tmp_path / "concept_mapping.csv"
    concept_input.write_text(
        "\n".join(
            [
                "trade_date,symbol,concept_id,concept_name,mapping_source,mapping_version,is_primary_concept,weight",
                "2025-01-02,AAA,AI_THEME,AI Theme,concept,v1,true,1.0",
                "2025-01-02,BBB,BAIJIU,Baijiu,concept,v1,false,0.4",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    config = BootstrapDerivedConfig(
        bars_csv=tmp_path / "bars.csv",
        mapping_input_csv=mapping_input,
        concept_mapping_input_csv=concept_input,
        mapping_output_csv=tmp_path / "sector_mapping_out.csv",
        sector_snapshots_output_csv=tmp_path / "sector_snapshots.csv",
        stock_snapshots_output_csv=tmp_path / "stock_snapshots.csv",
        mainline_windows_output_csv=tmp_path / "mainline_windows.csv",
        mapping_source="test",
        mapping_version="test_v1",
        protocol_version="protocol_v1.0",
        sector_assignments={},
        lookback=3,
        top_sector_score_threshold=0.3,
        top_sector_rank_limit=1,
        min_window_length=1,
    )

    mappings = BootstrapDerivedDataBuilder(config)._build_sector_mappings(bars)
    by_symbol = {record.symbol: record for record in mappings}

    assert by_symbol["AAA"].sector_id == "AI_THEME"
    assert by_symbol["AAA"].sector_name == "AI Theme"
    assert by_symbol["BBB"].sector_id == "CONSUMER"


def test_bootstrap_derived_can_boost_late_mover_quality_with_concept_support(tmp_path: Path) -> None:
    bars = [
        build_bar("2025-01-02", "AAA", 10.0, pre_close=9.8, turnover=220_000_000),
        build_bar("2025-01-03", "AAA", 10.5, pre_close=10.0, turnover=240_000_000),
        build_bar("2025-01-06", "AAA", 10.8, pre_close=10.5, turnover=250_000_000),
        build_bar("2025-01-02", "BBB", 10.0, pre_close=10.0, turnover=180_000_000),
        build_bar("2025-01-03", "BBB", 10.2, pre_close=10.0, turnover=190_000_000),
        build_bar("2025-01-06", "BBB", 10.4, pre_close=10.2, turnover=200_000_000),
    ]
    concept_input = tmp_path / "concept_mapping.csv"
    concept_input.write_text(
        "\n".join(
            [
                "trade_date,symbol,concept_id,concept_name,mapping_source,mapping_version,is_primary_concept,weight",
                "2025-01-06,AAA,C1,Concept 1,concept,v1,true,0.8",
                "2025-01-06,AAA,C2,Concept 2,concept,v1,false,0.3",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    base_config = BootstrapDerivedConfig(
        bars_csv=tmp_path / "bars.csv",
        mapping_input_csv=None,
        concept_mapping_input_csv=concept_input,
        mapping_output_csv=tmp_path / "sector_mapping.csv",
        sector_snapshots_output_csv=tmp_path / "sector_snapshots.csv",
        stock_snapshots_output_csv=tmp_path / "stock_snapshots.csv",
        mainline_windows_output_csv=tmp_path / "mainline_windows.csv",
        mapping_source="test",
        mapping_version="test_v1",
        protocol_version="protocol_v1.0",
        sector_assignments={
            "AAA": {"sector_id": "ALPHA", "sector_name": "Alpha"},
            "BBB": {"sector_id": "ALPHA", "sector_name": "Alpha"},
        },
        lookback=3,
        top_sector_score_threshold=0.3,
        top_sector_rank_limit=1,
        min_window_length=1,
        concept_support_late_quality_boost=0.0,
        concept_support_primary_weight_influence=0.7,
        concept_support_multi_concept_influence=0.3,
    )
    boosted_config = BootstrapDerivedConfig(
        bars_csv=base_config.bars_csv,
        mapping_input_csv=base_config.mapping_input_csv,
        concept_mapping_input_csv=base_config.concept_mapping_input_csv,
        mapping_output_csv=base_config.mapping_output_csv,
        sector_snapshots_output_csv=base_config.sector_snapshots_output_csv,
        stock_snapshots_output_csv=base_config.stock_snapshots_output_csv,
        mainline_windows_output_csv=base_config.mainline_windows_output_csv,
        mapping_source=base_config.mapping_source,
        mapping_version=base_config.mapping_version,
        protocol_version=base_config.protocol_version,
        sector_assignments=base_config.sector_assignments,
        lookback=base_config.lookback,
        top_sector_score_threshold=base_config.top_sector_score_threshold,
        top_sector_rank_limit=base_config.top_sector_rank_limit,
        min_window_length=base_config.min_window_length,
        concept_support_late_quality_boost=0.05,
        concept_support_primary_weight_influence=0.7,
        concept_support_multi_concept_influence=0.3,
    )

    base_builder = BootstrapDerivedDataBuilder(base_config)
    boosted_builder = BootstrapDerivedDataBuilder(boosted_config)
    mappings = base_builder._build_sector_mappings(bars)
    sector_snapshots = base_builder._build_sector_snapshots(bars, mappings)
    base_snapshots = base_builder._build_stock_snapshots(
        bars,
        mappings,
        sector_snapshots,
        base_builder._load_concept_records(),
    )
    boosted_snapshots = boosted_builder._build_stock_snapshots(
        bars,
        mappings,
        sector_snapshots,
        boosted_builder._load_concept_records(),
    )
    base_latest = next(item for item in base_snapshots if item.symbol == "AAA" and item.trade_date == date(2025, 1, 6))
    boosted_latest = next(item for item in boosted_snapshots if item.symbol == "AAA" and item.trade_date == date(2025, 1, 6))

    assert boosted_latest.late_mover_quality > base_latest.late_mover_quality
    assert boosted_latest.late_quality_raw_score == base_latest.late_quality_raw_score
    assert boosted_latest.late_quality_concept_boost > 0.0
    assert boosted_latest.late_mover_quality == round(
        boosted_latest.late_quality_raw_score + boosted_latest.late_quality_concept_boost,
        6,
    )
    assert boosted_latest.concept_support > 0.0
    assert boosted_latest.primary_concept_weight > 0.0
    assert boosted_latest.concept_count == 2
    assert boosted_latest.non_junk_composite_score >= boosted_latest.late_component_score


def test_bootstrap_derived_caps_concept_support_boost_within_band(tmp_path: Path) -> None:
    bars = [
        build_bar("2025-01-02", "AAA", 10.0, pre_close=9.8, turnover=220_000_000),
        build_bar("2025-01-03", "AAA", 10.5, pre_close=10.0, turnover=240_000_000),
        build_bar("2025-01-06", "AAA", 10.8, pre_close=10.5, turnover=250_000_000),
    ]
    concept_input = tmp_path / "concept_mapping.csv"
    concept_input.write_text(
        "\n".join(
            [
                "trade_date,symbol,concept_id,concept_name,mapping_source,mapping_version,is_primary_concept,weight",
                "2025-01-06,AAA,C1,Concept 1,concept,v1,true,1.0",
                "2025-01-06,AAA,C2,Concept 2,concept,v1,false,0.6",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    base_config = BootstrapDerivedConfig(
        bars_csv=tmp_path / "bars.csv",
        mapping_input_csv=None,
        concept_mapping_input_csv=concept_input,
        mapping_output_csv=tmp_path / "sector_mapping.csv",
        sector_snapshots_output_csv=tmp_path / "sector_snapshots.csv",
        stock_snapshots_output_csv=tmp_path / "stock_snapshots.csv",
        mainline_windows_output_csv=tmp_path / "mainline_windows.csv",
        mapping_source="test",
        mapping_version="test_v1",
        protocol_version="protocol_v1.0",
        sector_assignments={
            "AAA": {"sector_id": "ALPHA", "sector_name": "Alpha"},
        },
        lookback=3,
        top_sector_score_threshold=0.3,
        top_sector_rank_limit=1,
        min_window_length=1,
        concept_support_late_quality_boost=0.0,
        concept_support_primary_weight_influence=0.7,
        concept_support_multi_concept_influence=0.3,
    )

    base_builder = BootstrapDerivedDataBuilder(base_config)
    base_mappings = base_builder._build_sector_mappings(bars)
    base_sector_snapshots = base_builder._build_sector_snapshots(bars, base_mappings)
    base_snapshots = base_builder._build_stock_snapshots(
        bars,
        base_mappings,
        base_sector_snapshots,
        base_builder._load_concept_records(),
    )
    base_latest = next(item for item in base_snapshots if item.symbol == "AAA" and item.trade_date == date(2025, 1, 6))
    cap_upper = round(base_latest.late_mover_quality + 0.01, 6)

    config = BootstrapDerivedConfig(
        bars_csv=base_config.bars_csv,
        mapping_input_csv=base_config.mapping_input_csv,
        concept_mapping_input_csv=base_config.concept_mapping_input_csv,
        mapping_output_csv=base_config.mapping_output_csv,
        sector_snapshots_output_csv=base_config.sector_snapshots_output_csv,
        stock_snapshots_output_csv=base_config.stock_snapshots_output_csv,
        mainline_windows_output_csv=base_config.mainline_windows_output_csv,
        mapping_source=base_config.mapping_source,
        mapping_version=base_config.mapping_version,
        protocol_version=base_config.protocol_version,
        sector_assignments=base_config.sector_assignments,
        lookback=base_config.lookback,
        top_sector_score_threshold=base_config.top_sector_score_threshold,
        top_sector_rank_limit=base_config.top_sector_rank_limit,
        min_window_length=base_config.min_window_length,
        concept_support_late_quality_boost=0.2,
        concept_support_primary_weight_influence=0.7,
        concept_support_multi_concept_influence=0.3,
        concept_support_band_lower=0.0,
        concept_support_band_upper=cap_upper,
        concept_support_cap_to_band_upper=True,
    )

    builder = BootstrapDerivedDataBuilder(config)
    mappings = builder._build_sector_mappings(bars)
    sector_snapshots = builder._build_sector_snapshots(bars, mappings)
    snapshots = builder._build_stock_snapshots(
        bars,
        mappings,
        sector_snapshots,
        builder._load_concept_records(),
    )
    latest = next(item for item in snapshots if item.symbol == "AAA" and item.trade_date == date(2025, 1, 6))

    assert latest.late_mover_quality <= cap_upper
    assert latest.late_mover_quality >= base_latest.late_mover_quality


def test_bootstrap_derived_exposes_late_quality_residual_components(tmp_path: Path) -> None:
    bars = [
        build_bar("2025-01-02", "AAA", 10.0, pre_close=9.7, turnover=210_000_000),
        build_bar("2025-01-03", "AAA", 10.3, pre_close=10.0, turnover=230_000_000),
        build_bar("2025-01-06", "AAA", 10.7, pre_close=10.3, turnover=250_000_000),
    ]
    config = BootstrapDerivedConfig(
        bars_csv=tmp_path / "bars.csv",
        mapping_input_csv=None,
        concept_mapping_input_csv=None,
        mapping_output_csv=tmp_path / "sector_mapping.csv",
        sector_snapshots_output_csv=tmp_path / "sector_snapshots.csv",
        stock_snapshots_output_csv=tmp_path / "stock_snapshots.csv",
        mainline_windows_output_csv=tmp_path / "mainline_windows.csv",
        mapping_source="test",
        mapping_version="test_v1",
        protocol_version="protocol_v1.0",
        sector_assignments={"AAA": {"sector_id": "ALPHA", "sector_name": "Alpha"}},
        lookback=3,
        top_sector_score_threshold=0.3,
        top_sector_rank_limit=1,
        min_window_length=1,
    )

    builder = BootstrapDerivedDataBuilder(config)
    mappings = builder._build_sector_mappings(bars)
    sector_snapshots = builder._build_sector_snapshots(bars, mappings)
    snapshots = builder._build_stock_snapshots(bars, mappings, sector_snapshots)
    latest = next(item for item in snapshots if item.symbol == "AAA" and item.trade_date == date(2025, 1, 6))

    expected_raw = round(
        latest.late_quality_sector_contribution
        + latest.late_quality_stability_contribution
        + latest.late_quality_liquidity_contribution
        + latest.late_quality_lag_contribution
        + latest.late_quality_trend_contribution,
        6,
    )

    assert latest.late_quality_raw_score == expected_raw
    assert latest.late_quality_sector_strength > 0.0
    assert latest.late_quality_lag_balance > 0.0
    assert latest.late_quality_trend_support > 0.0
    assert latest.stability_volatility >= 0.0
    assert 0.0 <= latest.liquidity_turnover_share <= 1.0
    assert 0.0 <= latest.liquidity_turnover_rank <= 1.0
    assert 0.0 <= latest.liquidity_sector_turnover_share <= 1.0
    assert 0.0 <= latest.liquidity_sector_top_turnover_share <= 1.0
    assert 0.0 <= latest.liquidity_sector_mean_turnover_share <= 1.0
    assert 0.0 <= latest.liquidity_sector_turnover_share_gap <= 1.0
    assert latest.liquidity_sector_symbol_count >= 1
    assert latest.late_quality_concept_boost == 0.0
