from pathlib import Path

from a_share_quant.strategy.v127m_commercial_aerospace_phase_conditioned_drag_veto_audit_v1 import (
    V127MCommercialAerospacePhaseConditionedDragVetoAuditAnalyzer,
)


def test_v127m_phase_conditioned_drag_veto_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127MCommercialAerospacePhaseConditionedDragVetoAuditAnalyzer(repo_root).analyze()

    assert report.summary["reference_variant"] == "broad_half_reference"
    assert report.summary["drag_symbols_ranked"][:3] == ["688066", "002085", "688523"]
    assert len(report.variant_rows) == 5
    assert any(row["variant"] != "broad_half_reference" for row in report.variant_rows)
