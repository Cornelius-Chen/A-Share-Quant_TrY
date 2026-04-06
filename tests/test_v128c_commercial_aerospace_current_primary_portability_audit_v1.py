from pathlib import Path

from a_share_quant.strategy.v128c_commercial_aerospace_current_primary_portability_audit_v1 import (
    V128CCommercialAerospaceCurrentPrimaryPortabilityAuditAnalyzer,
)


def test_v128c_current_primary_portability_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V128CCommercialAerospaceCurrentPrimaryPortabilityAuditAnalyzer(repo_root).analyze()

    assert report.summary["current_primary_variant"] == "window_riskoff_full_weakdrift_075_impulse_half"
    assert len(report.symbol_delta_rows) >= 3
    assert len(report.period_rows) == 3
