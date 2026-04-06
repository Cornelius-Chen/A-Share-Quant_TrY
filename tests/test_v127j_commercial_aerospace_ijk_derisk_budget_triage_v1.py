from pathlib import Path

from a_share_quant.strategy.v127j_commercial_aerospace_ijk_derisk_budget_triage_v1 import (
    V127JCommercialAerospaceIJKDeriskBudgetTriageAnalyzer,
)


def test_v127j_derisk_budget_triage_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V127JCommercialAerospaceIJKDeriskBudgetTriageAnalyzer(repo_root).analyze()
    assert result.summary["authoritative_status"] == "symbol_phase_aware_derisk_budget_stopline"
