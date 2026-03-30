from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.context_feature_pack_a_conditioned_late_quality_acceptance import (
    ContextConditionedLateQualityAcceptanceAnalyzer,
    write_context_conditioned_late_quality_acceptance_report,
)


def test_conditioned_late_quality_acceptance_closes_non_material_branch(tmp_path: Path) -> None:
    control_payload = {
        "comparisons": [
            {
                "strategy_name": "mainline_trend_a",
                "summary": {
                    "total_return": 0.001,
                    "max_drawdown": 0.010,
                    "mainline_capture_ratio": 0.10,
                    "signal_count": 100,
                },
            },
            {
                "strategy_name": "mainline_trend_b",
                "summary": {
                    "total_return": 0.002,
                    "max_drawdown": 0.011,
                    "mainline_capture_ratio": 0.12,
                    "signal_count": 120,
                },
            },
            {
                "strategy_name": "mainline_trend_c",
                "summary": {
                    "total_return": 0.003,
                    "max_drawdown": 0.012,
                    "mainline_capture_ratio": 0.14,
                    "signal_count": 140,
                },
            },
        ]
    }
    conditioned_payload = {
        "comparisons": [
            {
                "strategy_name": "mainline_trend_a",
                "summary": {
                    "total_return": 0.001,
                    "max_drawdown": 0.010,
                    "mainline_capture_ratio": 0.10,
                    "signal_count": 100,
                },
            },
            {
                "strategy_name": "mainline_trend_b",
                "summary": {
                    "total_return": 0.0022,
                    "max_drawdown": 0.0109,
                    "mainline_capture_ratio": 0.12,
                    "signal_count": 121,
                },
            },
            {
                "strategy_name": "mainline_trend_c",
                "summary": {
                    "total_return": 0.0025,
                    "max_drawdown": 0.0123,
                    "mainline_capture_ratio": 0.139,
                    "signal_count": 145,
                },
            },
        ]
    }

    result = ContextConditionedLateQualityAcceptanceAnalyzer().analyze(
        control_payload=control_payload,
        conditioned_payload=conditioned_payload,
    )

    assert result.summary["acceptance_posture"] == (
        "close_conditioned_late_quality_branch_as_non_material"
    )
    assert result.summary["material_improvement_count"] == 0
    assert result.summary["harmed_strategy_count"] == 1
    output_path = write_context_conditioned_late_quality_acceptance_report(
        reports_dir=tmp_path,
        report_name="context_conditioned_late_quality_acceptance_test",
        result=result,
    )
    assert output_path.exists()
