from pathlib import Path

from a_share_quant.strategy.v134ft_commercial_aerospace_active_wave_selection_supervision_audit_v1 import (
    V134FTCommercialAerospaceActiveWaveSelectionSupervisionAuditV1Analyzer,
)


def test_v134ft_commercial_aerospace_active_wave_selection_supervision_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FTCommercialAerospaceActiveWaveSelectionSupervisionAuditV1Analyzer(repo_root).analyze()

    assert result.summary["active_wave_day_count"] == 2
    assert result.summary["candidate_count"] == 3
    assert result.summary["selected_candidate_count"] == 2
    assert result.summary["displaced_candidate_count"] == 1
    assert result.summary["recent_reduce_residue_displaced_count"] == 1
    assert result.summary["same_symbol_continuation_selected_count"] == 1
    assert result.summary["clean_reset_selected_count"] == 1
