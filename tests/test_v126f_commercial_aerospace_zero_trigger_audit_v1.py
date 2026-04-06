from pathlib import Path

from a_share_quant.strategy.v126f_commercial_aerospace_zero_trigger_audit_v1 import (
    V126FCommercialAerospaceZeroTriggerAuditAnalyzer,
)


def test_v126f_runs_zero_trigger_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V126FCommercialAerospaceZeroTriggerAuditAnalyzer(repo_root).analyze()
    assert result.summary["impulse_continuation_test_count"] >= 0
