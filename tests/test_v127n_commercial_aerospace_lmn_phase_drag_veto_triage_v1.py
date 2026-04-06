from pathlib import Path

from a_share_quant.strategy.v127n_commercial_aerospace_lmn_phase_drag_veto_triage_v1 import (
    V127NCommercialAerospaceLMNPhaseDragVetoTriageAnalyzer,
)


def test_v127n_phase_drag_veto_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127NCommercialAerospaceLMNPhaseDragVetoTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "promote_selective_phase_drag_veto_to_primary_reference"
    assert report.summary["new_primary_variant"] == "veto_drag_trio_impulse_only"
    assert len(report.subagent_rows) == 3
