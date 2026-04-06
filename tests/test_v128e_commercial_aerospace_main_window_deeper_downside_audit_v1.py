from pathlib import Path

from a_share_quant.strategy.v128e_commercial_aerospace_main_window_deeper_downside_audit_v1 import (
    V128ECommercialAerospaceMainWindowDeeperDownsideAuditAnalyzer,
)


def test_v128e_main_window_deeper_downside_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V128ECommercialAerospaceMainWindowDeeperDownsideAuditAnalyzer(repo_root).analyze()

    assert report.summary["reference_variant"] == "window_riskoff_full_weakdrift_075_impulse_half"
    assert len(report.variant_rows) == 5
