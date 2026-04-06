from pathlib import Path

from a_share_quant.strategy.v127u_commercial_aerospace_window_specific_derisk_grammar_audit_v1 import (
    V127UCommercialAerospaceWindowSpecificDeriskGrammarAuditAnalyzer,
)


def test_v127u_window_specific_derisk_grammar_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127UCommercialAerospaceWindowSpecificDeriskGrammarAuditAnalyzer(repo_root).analyze()

    assert report.summary["reference_variant"] == "veto_drag_trio_impulse_only"
    assert len(report.variant_rows) == 5
