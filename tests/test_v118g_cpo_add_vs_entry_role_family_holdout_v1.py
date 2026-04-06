from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v118g_cpo_add_vs_entry_role_family_holdout_v1 import (
    V118GCpoAddVsEntryRoleFamilyHoldoutAnalyzer,
)


def test_v118g_add_vs_entry_role_family_holdout() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V118GCpoAddVsEntryRoleFamilyHoldoutAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    assert result.summary["holdout_count"] >= 4
    assert result.summary["evaluable_holdout_count"] >= 2

