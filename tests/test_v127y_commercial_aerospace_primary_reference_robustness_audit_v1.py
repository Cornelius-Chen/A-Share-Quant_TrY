from pathlib import Path

from a_share_quant.strategy.v127y_commercial_aerospace_primary_reference_robustness_audit_v1 import (
    V127YCommercialAerospacePrimaryReferenceRobustnessAuditAnalyzer,
)


def test_v127y_primary_reference_robustness_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127YCommercialAerospacePrimaryReferenceRobustnessAuditAnalyzer(repo_root).analyze()

    assert report.summary["new_primary_variant"] == "window_riskoff_full_weakdrift_075_impulse_half"
    assert len(report.split_rows) == 4
    assert len(report.suffix_rows) == 4
