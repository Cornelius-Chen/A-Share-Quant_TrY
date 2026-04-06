from pathlib import Path

from a_share_quant.strategy.v127a_commercial_aerospace_phase_aware_derisk_audit_v1 import (
    V127ACommercialAerospacePhaseAwareDeriskAuditAnalyzer,
)


def test_v127a_phase_aware_derisk_audit_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V127ACommercialAerospacePhaseAwareDeriskAuditAnalyzer(repo_root).analyze()
    assert len(result.variant_rows) == 3
