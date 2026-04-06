from pathlib import Path

from a_share_quant.strategy.v134fr_commercial_aerospace_add_wave_state_authority_audit_v1 import (
    V134FRCommercialAerospaceAddWaveStateAuthorityAuditV1Analyzer,
)


def test_v134fr_commercial_aerospace_add_wave_state_authority_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FRCommercialAerospaceAddWaveStateAuthorityAuditV1Analyzer(repo_root).analyze()

    assert result.summary["candidate_day_count"] == 4
    assert result.summary["active_wave_selection_day_count"] == 2
    assert result.summary["post_wave_echo_guard_count"] == 2
    assert result.summary["post_wave_echo_authority_family_count"] == 2
