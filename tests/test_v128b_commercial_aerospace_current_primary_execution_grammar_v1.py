from pathlib import Path

from a_share_quant.strategy.v128b_commercial_aerospace_current_primary_execution_grammar_v1 import (
    V128BCommercialAerospaceCurrentPrimaryExecutionGrammarAnalyzer,
)


def test_v128b_current_primary_execution_grammar() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V128BCommercialAerospaceCurrentPrimaryExecutionGrammarAnalyzer(repo_root).analyze()

    assert report.summary["current_primary_variant"] == "window_riskoff_full_weakdrift_075_impulse_half"
    assert report.summary["execution_grammar_compaction"] == "entry_surface_stable_plus_window_specific_derisk_intensification"
    assert len(report.grammar_rows) >= 4
