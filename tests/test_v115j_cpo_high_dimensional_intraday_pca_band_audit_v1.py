from __future__ import annotations

import csv
from pathlib import Path

from a_share_quant.strategy.v115j_cpo_high_dimensional_intraday_pca_band_audit_v1 import (
    V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer,
)


def test_v115j_pca_band_audit_runs_and_produces_components() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    with (repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv").open("r", encoding="utf-8") as handle:
        training_view_rows = list(csv.DictReader(handle))

    analyzer = V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer(repo_root=repo_root)
    report, annotated_rows = analyzer.analyze(training_view_rows=training_view_rows)

    summary = report.summary
    assert summary["acceptance_posture"] == "freeze_v115j_cpo_high_dimensional_intraday_pca_band_audit_v1"
    assert summary["base_row_count"] == 450
    assert summary["feature_count"] > 25
    assert summary["component_count"] == 3
    assert summary["discovery_posture"] == "continuous_band_audit_before_discrete_clustering"
    assert len(annotated_rows) == 450


def test_v115j_annotated_rows_have_pca_scores_and_bands() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    with (repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv").open("r", encoding="utf-8") as handle:
        training_view_rows = list(csv.DictReader(handle))

    analyzer = V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer(repo_root=repo_root)
    _, annotated_rows = analyzer.analyze(training_view_rows=training_view_rows)

    first_row = annotated_rows[0]
    assert "pc1_score" in first_row
    assert "pc2_score" in first_row
    assert "pc3_score" in first_row
    assert "pc1_band" in first_row
    assert "pc2_band" in first_row
    assert "state_band" in first_row
