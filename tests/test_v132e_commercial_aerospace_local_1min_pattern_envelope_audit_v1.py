from pathlib import Path

from a_share_quant.strategy.v132e_commercial_aerospace_local_1min_pattern_envelope_audit_v1 import (
    V132ECommercialAerospaceLocal1MinPatternEnvelopeAuditAnalyzer,
)


def test_v132e_local_1min_pattern_envelope_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132ECommercialAerospaceLocal1MinPatternEnvelopeAuditAnalyzer(repo_root).analyze()

    assert result.summary["session_count"] == 6
    assert result.summary["severity_tier_count"] == 3
    assert len(result.tier_envelope_rows) == 3

