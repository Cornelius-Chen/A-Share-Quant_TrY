from __future__ import annotations

import csv
from pathlib import Path

from a_share_quant.strategy.v115i_cpo_high_dimensional_intraday_action_training_pilot_v1 import (
    V115ICpoHighDimensionalIntradayActionTrainingPilotAnalyzer,
)


def test_v115i_builds_balanced_training_view_and_candidate_models() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    with (repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv").open("r", encoding="utf-8") as handle:
        base_rows = list(csv.DictReader(handle))

    analyzer = V115ICpoHighDimensionalIntradayActionTrainingPilotAnalyzer(repo_root=repo_root)
    report, training_view_rows = analyzer.analyze(base_rows=base_rows)

    summary = report.summary
    assert summary["acceptance_posture"] == "freeze_v115i_cpo_high_dimensional_intraday_action_training_pilot_v1"
    assert summary["base_row_count"] == 450
    assert summary["train_row_count"] == 308
    assert summary["test_row_count"] == 142
    assert summary["coarse_label_count"] == 3
    assert summary["selected_feature_count"] == 12
    assert summary["smallest_train_class_count"] == 5
    assert summary["balanced_training_view_built"] is True
    assert summary["candidate_only_pilot"] is True
    assert len(training_view_rows) == 450


def test_v115i_training_view_contains_weights_and_coarse_labels() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    with (repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv").open("r", encoding="utf-8") as handle:
        base_rows = list(csv.DictReader(handle))

    analyzer = V115ICpoHighDimensionalIntradayActionTrainingPilotAnalyzer(repo_root=repo_root)
    _, training_view_rows = analyzer.analyze(base_rows=base_rows)

    first_row = training_view_rows[0]
    assert "coarse_label" in first_row
    assert "row_weight" in first_row
    assert "split_group" in first_row
    assert first_row["coarse_label"] in {"hold_or_skip", "increase_expression", "decrease_expression"}
