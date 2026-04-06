from pathlib import Path

from a_share_quant.strategy.v131s_commercial_aerospace_local_5min_override_prototype_audit_v1 import (
    V131SCommercialAerospaceLocal5MinOverridePrototypeAuditAnalyzer,
)


def test_v131s_commercial_aerospace_local_5min_override_prototype_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131SCommercialAerospaceLocal5MinOverridePrototypeAuditAnalyzer(repo_root).analyze()
    assert result.summary["override_positive_hit_count"] == result.summary["override_positive_total"] == 2
    assert result.summary["reversal_watch_hit_count"] == result.summary["reversal_watch_total"] == 2
    assert result.summary["clean_control_hit_count"] == 0
