from __future__ import annotations

from datetime import date
from pathlib import Path

from a_share_quant.common.models import DailyBar
from a_share_quant.data.concept_mapper import AkshareConceptMapper, ConceptMapperConfig


def _make_bar(trade_date: str, close: float, pre_close: float) -> DailyBar:
    return DailyBar(
        trade_date=date.fromisoformat(trade_date),
        symbol="AAA",
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1.0,
        turnover=1000.0,
        pre_close=pre_close,
        adjust_factor=1.0,
    )


def test_symbol_records_rotate_primary_concept_with_history() -> None:
    mapper = object.__new__(AkshareConceptMapper)
    mapper.config = ConceptMapperConfig(
        mapping_source="akshare_em_concept",
        mapping_version="concept_test_v2",
        output_csv=Path("unused.csv"),
        max_boards_to_scan=10,
        min_concepts_per_symbol=1,
        max_concepts_per_symbol=3,
        board_pause_seconds=0.0,
        use_board_history=True,
        history_period="daily",
        history_adjust="",
        history_start_date=None,
        history_end_date=None,
        min_export_weight=0.15,
        base_rank_weight=0.2,
        board_history_weight=0.6,
        stock_alignment_weight=0.2,
    )

    symbol_bars = [
        _make_bar("2024-01-02", 10.0, 9.5),
        _make_bar("2024-01-03", 9.7, 10.0),
    ]
    concept_hits = [
        {"concept_id": "C1", "concept_name": "Alpha", "board_rank": 1},
        {"concept_id": "C2", "concept_name": "Beta", "board_rank": 2},
    ]
    concept_history = {
        "C1": {
            date(2024, 1, 2): {"score": 0.9, "daily_return": 0.06, "trailing_return": 0.08},
            date(2024, 1, 3): {"score": 0.2, "daily_return": -0.03, "trailing_return": -0.02},
        },
        "C2": {
            date(2024, 1, 2): {"score": 0.3, "daily_return": 0.01, "trailing_return": 0.01},
            date(2024, 1, 3): {"score": 0.85, "daily_return": -0.05, "trailing_return": -0.04},
        },
    }

    records = mapper._build_symbol_records(
        symbol="AAA",
        symbol_bars=symbol_bars,
        concept_hits=concept_hits,
        concept_history=concept_history,
    )

    first_day_primary = [
        record.concept_name
        for record in records
        if record.trade_date == date(2024, 1, 2) and record.is_primary_concept
    ]
    second_day_primary = [
        record.concept_name
        for record in records
        if record.trade_date == date(2024, 1, 3) and record.is_primary_concept
    ]

    assert first_day_primary == ["Alpha"]
    assert second_day_primary == ["Beta"]


def test_symbol_records_filter_weak_secondary_concepts() -> None:
    mapper = object.__new__(AkshareConceptMapper)
    mapper.config = ConceptMapperConfig(
        mapping_source="akshare_em_concept",
        mapping_version="concept_test_v2",
        output_csv=Path("unused.csv"),
        max_boards_to_scan=10,
        min_concepts_per_symbol=1,
        max_concepts_per_symbol=4,
        board_pause_seconds=0.0,
        use_board_history=True,
        history_period="daily",
        history_adjust="",
        history_start_date=None,
        history_end_date=None,
        min_export_weight=0.25,
        base_rank_weight=0.2,
        board_history_weight=0.6,
        stock_alignment_weight=0.2,
    )

    symbol_bars = [_make_bar("2024-01-02", 10.0, 9.8)]
    concept_hits = [
        {"concept_id": "C1", "concept_name": "Alpha", "board_rank": 1},
        {"concept_id": "C2", "concept_name": "Beta", "board_rank": 5},
        {"concept_id": "C3", "concept_name": "Gamma", "board_rank": 9},
    ]
    concept_history = {
        "C1": {date(2024, 1, 2): {"score": 0.85, "daily_return": 0.03, "trailing_return": 0.05}},
        "C2": {date(2024, 1, 2): {"score": 0.22, "daily_return": 0.00, "trailing_return": 0.01}},
        "C3": {date(2024, 1, 2): {"score": 0.05, "daily_return": -0.01, "trailing_return": 0.00}},
    }

    records = mapper._build_symbol_records(
        symbol="AAA",
        symbol_bars=symbol_bars,
        concept_hits=concept_hits,
        concept_history=concept_history,
    )

    assert len(records) == 2
    assert sum(record.is_primary_concept for record in records) == 1
