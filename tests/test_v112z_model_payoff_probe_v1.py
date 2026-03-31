from pathlib import Path

from a_share_quant.strategy.v112z_model_payoff_probe_v1 import (
    V112ZModelPayoffProbeAnalyzer,
    load_json_report,
)


def test_v112z_model_payoff_probe_runs_on_frozen_pilot() -> None:
    analyzer = V112ZModelPayoffProbeAnalyzer()
    result = analyzer.analyze(
        operational_charter_payload=load_json_report(Path("reports/analysis/v112z_operational_charter_v1.json")),
        pilot_dataset_payload=load_json_report(Path("reports/analysis/v112b_pilot_dataset_freeze_v1.json")),
    )
    assert result.summary["model_count"] == 3
    assert result.summary["primary_positive_label"] == "carry_constructive"
    assert result.summary["formal_training_still_forbidden"] is True
    assert any(row["model_name"] == "hist_gradient_boosting_classifier_v2" for row in result.model_rows)
