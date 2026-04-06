from pathlib import Path

from a_share_quant.strategy.v131e_commercial_aerospace_intraday_override_case_control_audit_v1 import (
    V131ECommercialAerospaceIntradayOverrideCaseControlAuditAnalyzer,
)


def test_v131e_commercial_aerospace_intraday_override_case_control_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131ECommercialAerospaceIntradayOverrideCaseControlAuditAnalyzer(repo_root).analyze()

    assert result.summary["override_positive_count"] == 2
    assert result.summary["clean_control_count"] >= 20
    assert result.summary["override_signal_is_derisk_share"] == 1.0
    assert result.summary["override_no_preopen_adverse_share"] == 1.0
    assert result.summary["open_to_close_separation"] < 0
    assert result.summary["forward_return_10_separation"] < 0
