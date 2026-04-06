from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117c_cpo_quality_side_discriminator_discovery_v1 import (
    V117CCpoQualitySideDiscriminatorDiscoveryAnalyzer,
)


def test_v117c_quality_side_discovery() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117CCpoQualitySideDiscriminatorDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116z_payload=json.loads((repo_root / "reports" / "analysis" / "v116z_cpo_quality_side_cooled_refinement_v1.json").read_text(encoding="utf-8")),
        v116w_payload=json.loads((repo_root / "reports" / "analysis" / "v116w_cpo_corrected_cooled_shadow_expanded_window_validation_rebuilt_base_v1.json").read_text(encoding="utf-8")),
        rebuilt_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
    )

    assert result.summary["candidate_discriminator_name"] == "continuation_integrity_score_candidate"
    assert result.summary["candidate_score_mean_gap_q25_minus_hot_only"] > 0
    assert result.feature_separation_rows[0]["feature_name"] in {
        "pc1_score",
        "f60_high_time_ratio_rz",
        "f30_high_time_ratio_rz",
        "f60_close_location_rz",
        "f30_close_location_rz",
    }
