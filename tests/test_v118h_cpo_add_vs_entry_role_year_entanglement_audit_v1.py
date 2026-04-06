from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v118h_cpo_add_vs_entry_role_year_entanglement_audit_v1 import (
    V118HCpoAddVsEntryRoleYearEntanglementAuditAnalyzer,
)


def test_v118h_add_vs_entry_role_year_entanglement_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V118HCpoAddVsEntryRoleYearEntanglementAuditAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    assert result.summary["positive_add_role_year_count"] > 0
    assert result.summary["entry_role_year_count"] > 0
