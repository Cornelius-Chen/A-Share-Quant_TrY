from __future__ import annotations

from datetime import date
from pathlib import Path

from a_share_quant.common.models import StockSnapshot
from a_share_quant.strategy.context_feature_pack_a_conditioned_late_quality import (
    ContextConditionedLateQualityAnalyzer,
    write_context_conditioned_late_quality_report,
)


def _snapshot(
    *,
    trade_date: date,
    symbol: str,
    late_quality: float,
    raw_score: float,
    non_junk: float,
    resonance: float,
    interaction: float,
    theme_density: float,
    turnover_concentration: float,
) -> StockSnapshot:
    return StockSnapshot(
        trade_date=trade_date,
        symbol=symbol,
        sector_id="S1",
        sector_name="Sector",
        expected_upside=0.6,
        drive_strength=0.6,
        stability=0.6,
        liquidity=0.6,
        late_mover_quality=late_quality,
        resonance=resonance,
        non_junk_composite_score=non_junk,
        late_quality_raw_score=raw_score,
        context_theme_density=theme_density,
        context_turnover_concentration=turnover_concentration,
        context_theme_turnover_interaction=interaction,
    )


def test_conditioned_late_quality_prefers_context_branch_when_candidates_cluster(tmp_path: Path) -> None:
    snapshots = [
        _snapshot(
            trade_date=date(2024, 4, 10),
            symbol="AAA",
            late_quality=0.53,
            raw_score=0.51,
            non_junk=0.60,
            resonance=0.50,
            interaction=0.31,
            theme_density=0.42,
            turnover_concentration=0.56,
        ),
        _snapshot(
            trade_date=date(2024, 4, 11),
            symbol="AAA",
            late_quality=0.54,
            raw_score=0.52,
            non_junk=0.58,
            resonance=0.48,
            interaction=0.24,
            theme_density=0.35,
            turnover_concentration=0.52,
        ),
        _snapshot(
            trade_date=date(2024, 7, 10),
            symbol="BBB",
            late_quality=0.58,
            raw_score=0.58,
            non_junk=0.61,
            resonance=0.46,
            interaction=0.11,
            theme_density=0.0,
            turnover_concentration=0.28,
        ),
        _snapshot(
            trade_date=date(2024, 10, 10),
            symbol="CCC",
            late_quality=0.52,
            raw_score=0.50,
            non_junk=0.57,
            resonance=0.45,
            interaction=0.27,
            theme_density=0.10,
            turnover_concentration=0.61,
        ),
    ]
    for name, symbol in [("q2", "AAA"), ("q3", "BBB"), ("q4", "CCC")]:
        (tmp_path / f"{name}.json").write_text(
            f'{{"summary":{{"acceptance_posture":"close_{name}","top_positive_symbols":["{symbol}"]}}}}',
            encoding="utf-8",
        )

    result = ContextConditionedLateQualityAnalyzer().analyze(
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
        late_quality_threshold=0.55,
        non_junk_threshold=0.55,
        resonance_floor=0.40,
        high_interaction_threshold=0.25,
        medium_interaction_threshold=0.18,
        near_threshold_gap=0.05,
    )

    assert result.summary["candidate_row_count"] == 3
    assert result.summary["recommended_conditioning_branch"] == (
        "conditioned_late_quality_on_theme_turnover_context"
    )
    assert result.summary["recommended_conditioning_posture"] == (
        "continue_context_conditioning_branch"
    )
    assert result.summary["candidate_bucket_counts"]["interaction_high"] == 2
    assert result.summary["candidate_bucket_counts"]["interaction_mid"] == 1

    output_path = write_context_conditioned_late_quality_report(
        reports_dir=tmp_path,
        report_name="context_feature_pack_a_conditioned_late_quality_test",
        result=result,
    )
    assert output_path.exists()
