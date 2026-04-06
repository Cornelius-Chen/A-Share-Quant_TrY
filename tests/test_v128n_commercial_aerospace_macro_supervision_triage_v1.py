from pathlib import Path

from a_share_quant.strategy.v128n_commercial_aerospace_macro_supervision_triage_v1 import (
    V128NCommercialAerospaceMacroSupervisionTriageAnalyzer,
)


def test_v128n_commercial_aerospace_macro_supervision_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128NCommercialAerospaceMacroSupervisionTriageAnalyzer(repo_root).analyze()

    assert result.summary["current_primary_variant"] == "tail_weakdrift_full"
    assert result.summary["next_direction"] == "time_chain_and_pre_open_event_governance_before_any_new_local_alpha_tuning"
    assert any(row["theme"] == "pre_open_decisive_event_veto" for row in result.retained_rows)
    assert any(row["theme"] == "symbol_micro_tuning" for row in result.blocked_rows)
