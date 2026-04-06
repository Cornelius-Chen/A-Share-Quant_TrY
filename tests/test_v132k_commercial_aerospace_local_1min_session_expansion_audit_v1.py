from pathlib import Path

from a_share_quant.strategy.v132k_commercial_aerospace_local_1min_session_expansion_audit_v1 import (
    V132KCommercialAerospaceLocal1MinSessionExpansionAuditAnalyzer,
)


def test_v132k_local_1min_session_expansion_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132KCommercialAerospaceLocal1MinSessionExpansionAuditAnalyzer(repo_root).analyze()

    assert result.summary["seed_symbol_count"] == 6
    assert result.summary["expanded_session_count"] == 612

