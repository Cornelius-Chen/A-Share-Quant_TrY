from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v118b_cpo_add_vs_entry_discriminator_discovery_v1 import (
    V118BCpoAddVsEntryDiscriminatorDiscoveryAnalyzer,
)


def test_v118b_add_vs_entry_discovery() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V118BCpoAddVsEntryDiscriminatorDiscoveryAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
        carried_threshold=489402000.0,
    )
    assert result.summary["candidate_name"] == "add_vs_strong_entry_separation_score_candidate"
    assert result.summary["positive_add_row_count"] == 5
    assert result.summary["leaked_entry_row_count"] == 4
    assert result.summary["mean_gap_positive_add_minus_leaked_entry"] > 0

