from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v117k_cpo_reverse_signal_candidate_discovery_v1 import (
    V117KCpoReverseSignalCandidateDiscoveryAnalyzer,
)


def test_v117k_reverse_signal_discovery() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117KCpoReverseSignalCandidateDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
    )

    assert result.summary["candidate_discriminator_name"] == "continuation_failure_damage_score_candidate"
    assert result.summary["candidate_score_mean_gap_negative_minus_non_negative"] > 0
    assert result.feature_separation_rows[0]["feature_name"] in {
        "f60_high_time_ratio_rz",
        "f60_close_location_rz",
        "f30_close_location_rz",
        "f30_high_time_ratio_rz",
    }
