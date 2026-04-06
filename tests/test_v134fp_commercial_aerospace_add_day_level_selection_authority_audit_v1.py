from pathlib import Path

from a_share_quant.strategy.v134fp_commercial_aerospace_add_day_level_selection_authority_audit_v1 import (
    V134FPCommercialAerospaceAddDayLevelSelectionAuthorityAuditV1Analyzer,
)


def test_v134fp_commercial_aerospace_add_day_level_selection_authority_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FPCommercialAerospaceAddDayLevelSelectionAuthorityAuditV1Analyzer(repo_root).analyze()

    assert result.summary["candidate_day_count"] == 4
    assert result.summary["aligned_selection_day_count"] == 1
    assert result.summary["displaced_selection_day_count"] == 1
    assert result.summary["post_wave_echo_day_count"] == 2
