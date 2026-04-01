from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v115k_cpo_intraday_band_action_audit_v1 import (
    V115KCpoIntradayBandActionAuditAnalyzer,
)


def test_v115k_band_action_audit_shapes() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    with (repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_v1.csv").open("r", encoding="utf-8") as handle:
        annotated_rows = list(csv.DictReader(handle))
    analyzer = V115KCpoIntradayBandActionAuditAnalyzer(repo_root=repo_root)
    report, output_rows = analyzer.analyze(
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
        v115j_payload=json.loads((repo_root / "reports" / "analysis" / "v115j_cpo_high_dimensional_intraday_pca_band_audit_v1.json").read_text(encoding="utf-8")),
        annotated_rows=annotated_rows,
    )
    summary = report.summary
    assert summary["acceptance_posture"] == "freeze_v115k_cpo_intraday_band_action_audit_v1"
    assert summary["band_count"] >= 1
    assert summary["annotated_row_count"] == 450
    assert len(output_rows) == 450


def test_v115k_derives_candidate_band_postures() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    with (repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_v1.csv").open("r", encoding="utf-8") as handle:
        annotated_rows = list(csv.DictReader(handle))
    analyzer = V115KCpoIntradayBandActionAuditAnalyzer(repo_root=repo_root)
    report, _ = analyzer.analyze(
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
        v115j_payload=json.loads((repo_root / "reports" / "analysis" / "v115j_cpo_high_dimensional_intraday_pca_band_audit_v1.json").read_text(encoding="utf-8")),
        annotated_rows=annotated_rows,
    )
    band_postures = {row["band_posture"] for row in report.band_registry_rows}
    assert "candidate_add_band" in band_postures
    assert "candidate_reduce_band" in band_postures
