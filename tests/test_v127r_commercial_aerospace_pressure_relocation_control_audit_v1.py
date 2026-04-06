from pathlib import Path

from a_share_quant.strategy.v127r_commercial_aerospace_pressure_relocation_control_audit_v1 import (
    V127RCommercialAerospacePressureRelocationControlAuditAnalyzer,
)


def test_v127r_pressure_relocation_control_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127RCommercialAerospacePressureRelocationControlAuditAnalyzer(repo_root).analyze()

    assert report.summary["reference_variant"] == "veto_drag_trio_impulse_only"
    assert len(report.variant_rows) == 5
