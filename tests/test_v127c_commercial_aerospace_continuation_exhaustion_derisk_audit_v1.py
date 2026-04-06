from pathlib import Path

from a_share_quant.strategy.v127c_commercial_aerospace_continuation_exhaustion_derisk_audit_v1 import (
    V127CCommercialAerospaceContinuationExhaustionDeriskAuditAnalyzer,
)


def test_v127c_continuation_exhaustion_derisk_audit_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V127CCommercialAerospaceContinuationExhaustionDeriskAuditAnalyzer(repo_root).analyze()
    assert len(result.variant_rows) == 3
