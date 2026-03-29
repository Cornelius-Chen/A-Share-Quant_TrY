from __future__ import annotations

from datetime import date

from a_share_quant.common.models import MainlineWindow
from a_share_quant.strategy.late_mover_admissibility import (
    CandidateAdmissibilityState,
    LateMoverAdmissibilityAnalyzer,
)


def test_late_mover_admissibility_flags_blocked_and_partial_windows() -> None:
    analyzer = LateMoverAdmissibilityAnalyzer()
    windows = [
        MainlineWindow(
            window_id="w_blocked",
            symbol="AAA",
            start_date=date(2024, 9, 23),
            end_date=date(2024, 9, 30),
            capturable_return=0.30,
        ),
        MainlineWindow(
            window_id="w_partial",
            symbol="BBB",
            start_date=date(2024, 10, 1),
            end_date=date(2024, 10, 4),
            capturable_return=0.20,
        ),
    ]
    incumbent_state = CandidateAdmissibilityState(
        candidate_name="shared_default",
        window_breakdown_by_id={
            "w_blocked": {"window_id": "w_blocked", "capture_ratio": 1.0},
            "w_partial": {"window_id": "w_partial", "capture_ratio": 0.9},
        },
        gap_records_by_window_id={},
    )
    challenger_state = CandidateAdmissibilityState(
        candidate_name="challenger",
        window_breakdown_by_id={
            "w_blocked": {"window_id": "w_blocked", "capture_ratio": 0.0},
            "w_partial": {"window_id": "w_partial", "capture_ratio": 0.4},
        },
        gap_records_by_window_id={
            "w_blocked": [
                {
                    "trade_date": "2024-09-24",
                    "assignment_reason": "fallback_to_junk",
                    "layer_score": 0.91,
                    "late_score": 0.68,
                    "core_score": 0.32,
                    "passed_filters": ["strict_short_term_bullish"],
                    "triggered_entries": ["mid_trend_follow"],
                    "emitted_buy_signal": False,
                }
            ],
            "w_partial": [
                {
                    "trade_date": "2024-10-02",
                    "assignment_reason": "low_composite_or_low_resonance",
                    "layer_score": 0.66,
                    "late_score": 0.61,
                    "core_score": 0.41,
                    "passed_filters": ["loose_uptrend"],
                    "triggered_entries": ["confirmation_entry"],
                    "emitted_buy_signal": False,
                }
            ],
        },
    )

    strategy_delta, impacted_windows = analyzer._compare_strategy(
        strategy_name="mainline_trend_c",
        windows=windows,
        incumbent_state=incumbent_state,
        challenger_state=challenger_state,
    )

    assert strategy_delta["impacted_window_count"] == 2
    assert strategy_delta["blocked_window_count"] == 1
    assert strategy_delta["partial_window_count"] == 1
    assert impacted_windows[0]["classification"] == "blocked_window"
    assert impacted_windows[1]["classification"] == "partial_capture_with_admissibility_gap"
