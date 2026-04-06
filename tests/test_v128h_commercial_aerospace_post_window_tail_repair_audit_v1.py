from pathlib import Path

from a_share_quant.strategy.v128h_commercial_aerospace_post_window_tail_repair_audit_v1 import (
    V128HCommercialAerospacePostWindowTailRepairAuditAnalyzer,
)


def test_v128h_post_window_tail_repair_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V128HCommercialAerospacePostWindowTailRepairAuditAnalyzer(repo_root).analyze()

    assert report.summary["reference_variant"] == "mainwin_overdrive_075_impulse_075"
    assert len(report.variant_rows) == 5
