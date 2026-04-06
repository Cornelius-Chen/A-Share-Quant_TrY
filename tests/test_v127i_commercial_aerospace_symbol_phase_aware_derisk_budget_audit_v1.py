from pathlib import Path

from a_share_quant.strategy.v127i_commercial_aerospace_symbol_phase_aware_derisk_budget_audit_v1 import (
    V127ICommercialAerospaceSymbolPhaseAwareDeriskBudgetAuditAnalyzer,
)


def test_v127i_symbol_phase_aware_derisk_budget_audit_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V127ICommercialAerospaceSymbolPhaseAwareDeriskBudgetAuditAnalyzer(repo_root).analyze()
    assert len(result.variant_rows) == 4
