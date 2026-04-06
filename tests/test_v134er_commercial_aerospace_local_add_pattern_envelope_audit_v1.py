from pathlib import Path

from a_share_quant.strategy.v134er_commercial_aerospace_local_add_pattern_envelope_audit_v1 import (
    V134ERCommercialAerospaceLocalAddPatternEnvelopeAuditV1Analyzer,
)


def test_v134er_commercial_aerospace_local_add_pattern_envelope_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134ERCommercialAerospaceLocalAddPatternEnvelopeAuditV1Analyzer(repo_root).analyze()

    assert result.summary["label_tier_count"] == 4
    assert result.summary["separation_pair_count"] == 3

    separation = {row["comparison"]: row for row in result.separation_rows}
    assert separation["allowed_preheat_full_vs_allowed_preheat_probe"]["open_to_15m_gap"] > 0
    assert separation["failed_impulse_chase_vs_allowed_preheat_full"]["open_to_5m_gap"] < 0
    assert separation["blocked_board_lockout_vs_failed_impulse_chase"]["open_to_15m_gap"] > 0
