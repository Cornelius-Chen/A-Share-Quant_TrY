from pathlib import Path

from a_share_quant.strategy.v125o_commercial_aerospace_event_control_regime_audit_v1 import (
    V125OCommercialAerospaceEventControlRegimeAuditAnalyzer,
)


def test_v125o_reports_regime_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125OCommercialAerospaceEventControlRegimeAuditAnalyzer(repo_root).analyze()
    assert result.summary["regime_count"] >= 3
