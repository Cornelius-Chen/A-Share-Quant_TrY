from pathlib import Path

from a_share_quant.strategy.v127l_commercial_aerospace_jkl_drag_veto_triage_v1 import (
    V127LCommercialAerospaceJKLDragVetoTriageAnalyzer,
)


def test_v127l_drag_veto_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127LCommercialAerospaceJKLDragVetoTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "blocked_do_not_replace_cleaner_slot"
    assert report.summary["next_step"] == "phase_conditioned_drag_veto_audit"
    assert len(report.subagent_rows) == 3
