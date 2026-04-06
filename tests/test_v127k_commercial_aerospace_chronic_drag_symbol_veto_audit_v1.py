from pathlib import Path

from a_share_quant.strategy.v127k_commercial_aerospace_chronic_drag_symbol_veto_audit_v1 import (
    V127KCommercialAerospaceChronicDragSymbolVetoAuditAnalyzer,
)


def test_v127k_chronic_drag_symbol_veto_audit_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V127KCommercialAerospaceChronicDragSymbolVetoAuditAnalyzer(repo_root).analyze()
    assert len(result.variant_rows) == 4
