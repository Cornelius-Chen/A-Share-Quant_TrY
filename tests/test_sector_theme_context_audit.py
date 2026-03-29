from __future__ import annotations

from datetime import date
from pathlib import Path

from a_share_quant.common.models import SectorSnapshot, StockSnapshot
from a_share_quant.strategy.sector_theme_context_audit import (
    SectorThemeContextAuditAnalyzer,
    write_sector_theme_context_audit_report,
)


def _stock_snapshot(
    *,
    trade_date: date,
    symbol: str,
    sector_id: str,
    concept_support: float,
    concept_count: int,
    top_share: float,
    gap: float,
    late_quality_raw_score: float,
) -> StockSnapshot:
    return StockSnapshot(
        trade_date=trade_date,
        symbol=symbol,
        sector_id=sector_id,
        sector_name=sector_id,
        expected_upside=0.5,
        drive_strength=0.5,
        stability=0.5,
        liquidity=0.5,
        late_mover_quality=0.5,
        resonance=0.5,
        concept_support=concept_support,
        primary_concept_weight=concept_support,
        concept_count=concept_count,
        concept_concentration_ratio=concept_support,
        late_quality_raw_score=late_quality_raw_score,
        liquidity_sector_top_turnover_share=top_share,
        liquidity_sector_turnover_share_gap=gap,
    )


def _sector_snapshot(
    *,
    trade_date: date,
    sector_id: str,
    persistence: float,
    diffusion: float,
    money_making: float,
    leader_strength: float,
    relative_strength: float,
    activity: float,
) -> SectorSnapshot:
    return SectorSnapshot(
        trade_date=trade_date,
        sector_id=sector_id,
        sector_name=sector_id,
        persistence=persistence,
        diffusion=diffusion,
        money_making=money_making,
        leader_strength=leader_strength,
        relative_strength=relative_strength,
        activity=activity,
    )


def test_sector_theme_context_audit_prefers_theme_load_and_turnover_group(tmp_path: Path) -> None:
    stock_snapshots = [
        _stock_snapshot(
            trade_date=date(2024, 4, 10),
            symbol="AAA",
            sector_id="S1",
            concept_support=0.65,
            concept_count=3,
            top_share=0.78,
            gap=0.08,
            late_quality_raw_score=0.43,
        ),
        _stock_snapshot(
            trade_date=date(2024, 7, 10),
            symbol="BBB",
            sector_id="S2",
            concept_support=0.22,
            concept_count=1,
            top_share=0.52,
            gap=0.01,
            late_quality_raw_score=0.44,
        ),
        _stock_snapshot(
            trade_date=date(2024, 10, 10),
            symbol="CCC",
            sector_id="S3",
            concept_support=0.15,
            concept_count=1,
            top_share=0.81,
            gap=0.03,
            late_quality_raw_score=0.41,
        ),
    ]
    sector_snapshots = [
        _sector_snapshot(
            trade_date=date(2024, 4, 10),
            sector_id="S1",
            persistence=0.42,
            diffusion=0.44,
            money_making=0.48,
            leader_strength=0.47,
            relative_strength=0.46,
            activity=0.75,
        ),
        _sector_snapshot(
            trade_date=date(2024, 7, 10),
            sector_id="S2",
            persistence=0.56,
            diffusion=0.54,
            money_making=0.6,
            leader_strength=0.61,
            relative_strength=0.58,
            activity=0.57,
        ),
        _sector_snapshot(
            trade_date=date(2024, 10, 10),
            sector_id="S3",
            persistence=0.5,
            diffusion=0.49,
            money_making=0.45,
            leader_strength=0.44,
            relative_strength=0.46,
            activity=0.82,
        ),
    ]
    slice_specs = [
        {
            "dataset_name": "market_research_v1",
            "slice_name": "2024_q2",
            "slice_role": "capture",
            "acceptance_report_path": tmp_path / "q2.json",
        },
        {
            "dataset_name": "market_research_v1",
            "slice_name": "2024_q3",
            "slice_role": "drawdown",
            "acceptance_report_path": tmp_path / "q3.json",
        },
        {
            "dataset_name": "market_research_v1",
            "slice_name": "2024_q4",
            "slice_role": "drawdown",
            "acceptance_report_path": tmp_path / "q4.json",
        },
    ]
    (tmp_path / "q2.json").write_text(
        '{"summary":{"acceptance_posture":"close_q2","top_positive_symbols":["AAA"]}}',
        encoding="utf-8",
    )
    (tmp_path / "q3.json").write_text(
        '{"summary":{"acceptance_posture":"close_q3","shared_top_driver":"BBB"}}',
        encoding="utf-8",
    )
    (tmp_path / "q4.json").write_text(
        '{"summary":{"acceptance_posture":"close_q4","top_positive_symbols":["CCC"]}}',
        encoding="utf-8",
    )

    result = SectorThemeContextAuditAnalyzer().analyze(
        stock_snapshots=stock_snapshots,
        sector_snapshots=sector_snapshots,
        slice_specs=slice_specs,
    )

    assert result.summary["slice_count"] == 3
    assert result.summary["recommended_first_conditional_feature_group"] == (
        "theme_load_plus_turnover_concentration_context"
    )
    assert result.summary["recommended_second_conditional_feature_group"] == (
        "sector_state_heat_breadth_context"
    )
    assert result.axis_rankings[0]["axis_name"] in {
        "concept_support_mean",
        "theme_density_mean",
        "sector_top_turnover_share_mean",
    }

    output_path = write_sector_theme_context_audit_report(
        reports_dir=tmp_path,
        report_name="sector_theme_context_audit_test",
        result=result,
    )
    assert output_path.exists()
