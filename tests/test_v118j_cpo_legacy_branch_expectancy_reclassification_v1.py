from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v118j_cpo_legacy_branch_expectancy_reclassification_v1 import (
    V118JCpoLegacyBranchExpectancyReclassificationAnalyzer,
)


def test_v118j_legacy_branch_expectancy_reclassification() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V118JCpoLegacyBranchExpectancyReclassificationAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["soft_expectancy_component_count"] == 1
    assert result.summary["restored_soft_expectancy_branch"] == "breakout_damage"
    assert any(row["branch_name"] == "breakout_damage" and row["new_classification"] == "soft_expectancy_component" for row in result.branch_rows)
