from __future__ import annotations

from a_share_quant.strategy.cycle_mechanism_analysis import CycleMechanismAnalyzer


def test_classifies_entry_suppression_avoidance_for_avoided_negative_cycle() -> None:
    bridge_payload = {
        "bridged_cycles": [
            {
                "incumbent_cycle": {
                    "entry_date": "2024-08-01",
                    "exit_date": "2024-08-02",
                    "pnl": -100.0,
                },
                "classification": "avoided_cycle",
                "challenger_cycles": [],
            }
        ]
    }
    timeline_payload = {
        "candidate_records": [
            {
                "strategy_name": "mainline_trend_b",
                "candidate_name": "shared_default",
                "daily_records": [
                    {"trade_date": "2024-07-31", "emitted_actions": ["buy"]},
                    {"trade_date": "2024-08-01", "emitted_actions": ["sell"]},
                ],
            },
            {
                "strategy_name": "mainline_trend_b",
                "candidate_name": "theme_strict_quality_branch",
                "daily_records": [
                    {"trade_date": "2024-07-31", "emitted_actions": []},
                    {"trade_date": "2024-08-01", "emitted_actions": []},
                ],
            },
        ]
    }

    result = CycleMechanismAnalyzer().analyze(
        bridge_payload=bridge_payload,
        timeline_payload=timeline_payload,
        strategy_name="mainline_trend_b",
        incumbent_name="shared_default",
        challenger_name="theme_strict_quality_branch",
    )

    row = result.mechanism_rows[0]
    assert row["mechanism_type"] == "entry_suppression_avoidance"
    assert row["trigger_date"] == "2024-07-31"


def test_classifies_earlier_exit_loss_reduction() -> None:
    bridge_payload = {
        "bridged_cycles": [
            {
                "incumbent_cycle": {
                    "entry_date": "2024-08-09",
                    "exit_date": "2024-08-14",
                    "pnl": -300.0,
                },
                "classification": "reduced_loss_nearby_cycle",
                "closest_challenger_cycle": {
                    "entry_date": "2024-08-09",
                    "exit_date": "2024-08-13",
                    "pnl": -200.0,
                },
                "pnl_delta_vs_closest": 100.0,
            }
        ]
    }
    timeline_payload = {
        "candidate_records": [
            {
                "strategy_name": "mainline_trend_b",
                "candidate_name": "shared_default",
                "daily_records": [
                    {"trade_date": "2024-08-12", "emitted_actions": []},
                    {"trade_date": "2024-08-13", "emitted_actions": ["sell"]},
                ],
            },
            {
                "strategy_name": "mainline_trend_b",
                "candidate_name": "theme_strict_quality_branch",
                "daily_records": [
                    {"trade_date": "2024-08-12", "emitted_actions": ["sell"]},
                    {"trade_date": "2024-08-13", "emitted_actions": []},
                ],
            },
        ]
    }

    result = CycleMechanismAnalyzer().analyze(
        bridge_payload=bridge_payload,
        timeline_payload=timeline_payload,
        strategy_name="mainline_trend_b",
        incumbent_name="shared_default",
        challenger_name="theme_strict_quality_branch",
    )

    row = result.mechanism_rows[0]
    assert row["mechanism_type"] == "earlier_exit_loss_reduction"
    assert row["trigger_date"] == "2024-08-12"


def test_classifies_later_exit_loss_extension() -> None:
    bridge_payload = {
        "bridged_cycles": [
            {
                "incumbent_cycle": {
                    "entry_date": "2024-07-03",
                    "exit_date": "2024-07-05",
                    "pnl": -100.0,
                },
                "classification": "worse_nearby_cycle",
                "closest_challenger_cycle": {
                    "entry_date": "2024-07-03",
                    "exit_date": "2024-07-08",
                    "pnl": -250.0,
                },
                "pnl_delta_vs_closest": -150.0,
            }
        ]
    }
    timeline_payload = {
        "candidate_records": [
            {
                "strategy_name": "mainline_trend_b",
                "candidate_name": "shared_default",
                "daily_records": [
                    {"trade_date": "2024-07-04", "emitted_actions": ["sell"]},
                    {"trade_date": "2024-07-05", "emitted_actions": []},
                ],
            },
            {
                "strategy_name": "mainline_trend_b",
                "candidate_name": "theme_strict_quality_branch",
                "daily_records": [
                    {"trade_date": "2024-07-04", "emitted_actions": []},
                    {"trade_date": "2024-07-05", "emitted_actions": ["sell"]},
                ],
            },
        ]
    }

    result = CycleMechanismAnalyzer().analyze(
        bridge_payload=bridge_payload,
        timeline_payload=timeline_payload,
        strategy_name="mainline_trend_b",
        incumbent_name="shared_default",
        challenger_name="theme_strict_quality_branch",
    )

    row = result.mechanism_rows[0]
    assert row["mechanism_type"] == "later_exit_loss_extension"
    assert row["trigger_date"] == "2024-07-04"


def test_classifies_preemptive_loss_avoidance_shift() -> None:
    bridge_payload = {
        "bridged_cycles": [
            {
                "incumbent_cycle": {
                    "entry_date": "2024-12-13",
                    "exit_date": "2024-12-16",
                    "pnl": -300.0,
                },
                "classification": "reduced_loss_nearby_cycle",
                "closest_challenger_cycle": {
                    "entry_date": "2024-12-11",
                    "exit_date": "2024-12-12",
                    "pnl": -100.0,
                },
                "pnl_delta_vs_closest": 200.0,
            }
        ]
    }
    timeline_payload = {
        "candidate_records": [
            {
                "strategy_name": "mainline_trend_c",
                "candidate_name": "shared_default",
                "daily_records": [
                    {"trade_date": "2024-12-13", "emitted_actions": ["buy"]},
                ],
            },
            {
                "strategy_name": "mainline_trend_c",
                "candidate_name": "theme_strict_quality_branch",
                "daily_records": [
                    {"trade_date": "2024-12-11", "emitted_actions": ["buy"]},
                    {"trade_date": "2024-12-12", "emitted_actions": ["sell"]},
                ],
            },
        ]
    }

    result = CycleMechanismAnalyzer().analyze(
        bridge_payload=bridge_payload,
        timeline_payload=timeline_payload,
        strategy_name="mainline_trend_c",
        incumbent_name="shared_default",
        challenger_name="theme_strict_quality_branch",
    )

    row = result.mechanism_rows[0]
    assert row["mechanism_type"] == "preemptive_loss_avoidance_shift"
    assert row["trigger_date"] == "2024-12-11"


def test_classifies_carry_in_basis_advantage() -> None:
    bridge_payload = {
        "bridged_cycles": [
            {
                "incumbent_cycle": {
                    "entry_date": "2024-11-06",
                    "exit_date": "2024-11-07",
                    "pnl": -139.0,
                },
                "classification": "reduced_loss_nearby_cycle",
                "closest_challenger_cycle": {
                    "entry_date": "2024-11-05",
                    "exit_date": "2024-11-07",
                    "pnl": 702.0,
                },
                "pnl_delta_vs_closest": 841.0,
            }
        ]
    }
    timeline_payload = {
        "candidate_records": [
            {
                "strategy_name": "mainline_trend_c",
                "candidate_name": "shared_default",
                "daily_records": [
                    {"trade_date": "2024-11-05", "emitted_actions": ["buy"]},
                    {"trade_date": "2024-11-06", "emitted_actions": ["sell"]},
                ],
            },
            {
                "strategy_name": "mainline_trend_c",
                "candidate_name": "theme_strict_quality_branch",
                "daily_records": [
                    {"trade_date": "2024-11-04", "emitted_actions": ["buy"]},
                    {"trade_date": "2024-11-06", "emitted_actions": ["sell"]},
                ],
            },
        ]
    }

    result = CycleMechanismAnalyzer().analyze(
        bridge_payload=bridge_payload,
        timeline_payload=timeline_payload,
        strategy_name="mainline_trend_c",
        incumbent_name="shared_default",
        challenger_name="theme_strict_quality_branch",
    )

    row = result.mechanism_rows[0]
    assert row["mechanism_type"] == "carry_in_basis_advantage"
    assert row["trigger_date"] == "2024-11-05"


def test_classifies_delayed_entry_basis_advantage() -> None:
    bridge_payload = {
        "bridged_cycles": [
            {
                "incumbent_cycle": {
                    "entry_date": "2024-05-20",
                    "exit_date": "2024-05-22",
                    "pnl": -501.0,
                },
                "classification": "reduced_loss_nearby_cycle",
                "closest_challenger_cycle": {
                    "entry_date": "2024-05-21",
                    "exit_date": "2024-05-22",
                    "pnl": -148.0,
                },
                "pnl_delta_vs_closest": 353.0,
            }
        ]
    }
    timeline_payload = {
        "candidate_records": [
            {
                "strategy_name": "mainline_trend_c",
                "candidate_name": "shared_default",
                "daily_records": [
                    {"trade_date": "2024-05-20", "emitted_actions": ["buy"]},
                    {"trade_date": "2024-05-22", "emitted_actions": ["sell"]},
                ],
            },
            {
                "strategy_name": "mainline_trend_c",
                "candidate_name": "theme_strict_quality_branch",
                "daily_records": [
                    {"trade_date": "2024-05-21", "emitted_actions": ["buy"]},
                    {"trade_date": "2024-05-22", "emitted_actions": ["sell"]},
                ],
            },
        ]
    }

    result = CycleMechanismAnalyzer().analyze(
        bridge_payload=bridge_payload,
        timeline_payload=timeline_payload,
        strategy_name="mainline_trend_c",
        incumbent_name="shared_default",
        challenger_name="theme_strict_quality_branch",
    )

    row = result.mechanism_rows[0]
    assert row["mechanism_type"] == "delayed_entry_basis_advantage"
    assert row["trigger_date"] == "2024-05-21"
