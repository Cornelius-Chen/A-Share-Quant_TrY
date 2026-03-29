from __future__ import annotations

from datetime import date
from pathlib import Path

from a_share_quant.common.models import StockSnapshot
from a_share_quant.strategy.context_feature_pack_a import (
    ContextFeaturePackAAnalyzer,
    write_context_feature_pack_a_report,
)


def _snapshot(
    *,
    trade_date: date,
    symbol: str,
    theme_density: float,
    turnover_concentration: float,
    interaction: float,
    heat: float,
    breadth: float,
) -> StockSnapshot:
    return StockSnapshot(
        trade_date=trade_date,
        symbol=symbol,
        sector_id="S1",
        sector_name="Sector",
        expected_upside=0.5,
        drive_strength=0.5,
        stability=0.5,
        liquidity=0.5,
        late_mover_quality=0.5,
        resonance=0.5,
        context_theme_density=theme_density,
        context_turnover_concentration=turnover_concentration,
        context_theme_turnover_interaction=interaction,
        context_sector_heat=heat,
        context_sector_breadth=breadth,
    )


def test_context_feature_pack_a_prefers_theme_turnover_branch(tmp_path: Path) -> None:
    snapshots = [
        _snapshot(
            trade_date=date(2024, 4, 10),
            symbol="AAA",
            theme_density=0.42,
            turnover_concentration=0.76,
            interaction=0.56,
            heat=0.49,
            breadth=0.46,
        ),
        _snapshot(
            trade_date=date(2024, 7, 10),
            symbol="BBB",
            theme_density=0.23,
            turnover_concentration=0.55,
            interaction=0.36,
            heat=0.57,
            breadth=0.51,
        ),
        _snapshot(
            trade_date=date(2024, 10, 10),
            symbol="CCC",
            theme_density=0.16,
            turnover_concentration=0.79,
            interaction=0.41,
            heat=0.48,
            breadth=0.49,
        ),
    ]
    for name, symbol in [("q2", "AAA"), ("q3", "BBB"), ("q4", "CCC")]:
        (tmp_path / f"{name}.json").write_text(
            f'{{"summary":{{"acceptance_posture":"close_{name}","top_positive_symbols":["{symbol}"]}}}}',
            encoding="utf-8",
        )

    result = ContextFeaturePackAAnalyzer().analyze(
        stock_snapshots=snapshots,
        slice_specs=[
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
        ],
    )

    assert result.summary["slice_count"] == 3
    assert result.summary["recommended_next_feature_branch"] == (
        "conditioned_late_quality_on_theme_turnover_context"
    )
    assert result.summary["defer_sector_heat_branch"] is True
    assert {row["context_bucket"] for row in result.slice_rows} == {
        "interaction_high",
        "sector_heat_led",
        "turnover_led_theme_light",
    }

    output_path = write_context_feature_pack_a_report(
        reports_dir=tmp_path,
        report_name="context_feature_pack_a_test",
        result=result,
    )
    assert output_path.exists()
