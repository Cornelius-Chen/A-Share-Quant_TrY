from __future__ import annotations

from datetime import date
from pathlib import Path

from a_share_quant.common.models import StockSnapshot
from a_share_quant.strategy.context_feature_pack_b_sector_heat_breadth import (
    ContextFeaturePackBSectorHeatBreadthAnalyzer,
    write_context_feature_pack_b_report,
)


def _snapshot(
    *,
    trade_date: date,
    symbol: str,
    non_junk: float,
    late_quality: float,
    resonance: float,
    sector_heat: float,
    sector_breadth: float,
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
        late_mover_quality=late_quality,
        resonance=resonance,
        non_junk_composite_score=non_junk,
        context_sector_heat=sector_heat,
        context_sector_breadth=sector_breadth,
    )


def test_context_feature_pack_b_closes_sparse_sector_heat_branch(tmp_path: Path) -> None:
    snapshots = [
        _snapshot(
            trade_date=date(2024, 4, 10),
            symbol="AAA",
            non_junk=0.58,
            late_quality=0.57,
            resonance=0.48,
            sector_heat=0.52,
            sector_breadth=0.44,
        ),
        _snapshot(
            trade_date=date(2024, 8, 20),
            symbol="BBB",
            non_junk=0.60,
            late_quality=0.59,
            resonance=0.50,
            sector_heat=0.68,
            sector_breadth=0.58,
        ),
        _snapshot(
            trade_date=date(2024, 10, 24),
            symbol="CCC",
            non_junk=0.525,
            late_quality=0.56,
            resonance=0.55,
            sector_heat=0.80,
            sector_breadth=0.60,
        ),
    ]
    for name, symbol in [("q2", "AAA"), ("q3", "BBB"), ("q4", "CCC")]:
        (tmp_path / f"{name}.json").write_text(
            f'{{"summary":{{"acceptance_posture":"close_{name}","top_positive_symbols":["{symbol}"]}}}}',
            encoding="utf-8",
        )

    result = ContextFeaturePackBSectorHeatBreadthAnalyzer().analyze(
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
        non_junk_threshold=0.55,
        late_quality_floor=0.55,
        resonance_floor=0.40,
        high_sector_heat_threshold=0.65,
        high_sector_breadth_threshold=0.55,
        near_threshold_gap=0.05,
    )

    assert result.summary["candidate_row_count"] == 1
    assert result.summary["candidate_slice_names"] == ["2024_q4"]
    assert result.summary["recommended_next_feature_branch"] == (
        "close_sector_heat_breadth_context_branch_as_sparse"
    )
    assert result.summary["do_continue_context_feature_pack_b"] is False
    assert result.candidate_rows[0]["context_bucket"] == "heat_breadth_high"

    output_path = write_context_feature_pack_b_report(
        reports_dir=tmp_path,
        report_name="context_feature_pack_b_test",
        result=result,
    )
    assert output_path.exists()
