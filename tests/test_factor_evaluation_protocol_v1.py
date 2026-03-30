from __future__ import annotations

from a_share_quant.strategy.factor_evaluation_protocol_v1 import (
    FactorEvaluationProtocolAnalyzer,
)


def test_factor_evaluation_protocol_assigns_all_three_buckets() -> None:
    registry_payload = {
        "registry_rows": [
            {"entry_name": "carry_in_basis_advantage", "bucket": "candidate_factor"},
            {"entry_name": "preemptive_loss_avoidance_shift", "bucket": "candidate_factor"},
            {"entry_name": "delayed_entry_basis_advantage", "bucket": "candidate_factor"},
        ]
    }
    family_inventory_payload = {
        "family_rows": [
            {
                "family_name": "carry_in_basis_advantage",
                "occurrence_count": 2,
                "report_count": 2,
                "net_family_edge": 1682.5,
                "positive_opportunity_cost": 0.0,
            },
            {
                "family_name": "preemptive_loss_avoidance_shift",
                "occurrence_count": 2,
                "report_count": 2,
                "net_family_edge": 2475.7,
                "positive_opportunity_cost": 0.0,
            },
            {
                "family_name": "delayed_entry_basis_advantage",
                "occurrence_count": 1,
                "report_count": 1,
                "net_family_edge": 353.1,
                "positive_opportunity_cost": 0.0,
            },
        ],
        "pocket_rows": [
            {
                "family_counts": {"carry_in_basis_advantage": 1},
                "net_family_edge": 1464.4,
            },
            {
                "family_counts": {"carry_in_basis_advantage": 1},
                "net_family_edge": 1464.4,
            },
            {
                "family_counts": {
                    "preemptive_loss_avoidance_shift": 1,
                    "entry_suppression_opportunity_cost": 1,
                },
                "net_family_edge": -3294.9,
            },
            {
                "family_counts": {
                    "preemptive_loss_avoidance_shift": 1,
                    "entry_suppression_opportunity_cost": 1,
                },
                "net_family_edge": -28613.9,
            },
            {
                "family_counts": {"delayed_entry_basis_advantage": 1},
                "net_family_edge": -119.2,
            },
        ],
    }

    result = FactorEvaluationProtocolAnalyzer().analyze(
        registry_payload=registry_payload,
        family_inventory_payload=family_inventory_payload,
    )

    buckets = {row.entry_name: row.evaluation_bucket for row in result.factor_rows}
    assert buckets["carry_in_basis_advantage"] == "evaluate_now"
    assert buckets["preemptive_loss_avoidance_shift"] == "evaluate_with_penalty"
    assert buckets["delayed_entry_basis_advantage"] == "hold_for_more_sample"
    assert result.summary["ready_for_first_pass_factor_evaluation"] is True


def test_factor_evaluation_protocol_requires_inventory_row() -> None:
    registry_payload = {
        "registry_rows": [
            {"entry_name": "missing_factor", "bucket": "candidate_factor"},
        ]
    }
    family_inventory_payload = {"family_rows": [], "pocket_rows": []}

    try:
        FactorEvaluationProtocolAnalyzer().analyze(
            registry_payload=registry_payload,
            family_inventory_payload=family_inventory_payload,
        )
    except ValueError as exc:
        assert "Missing family inventory row" in str(exc)
    else:
        raise AssertionError("Expected a missing inventory row failure.")
