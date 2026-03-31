from pathlib import Path

from a_share_quant.strategy.v112m_phase_charter_v1 import V112MPhaseCharterAnalyzer, load_json_report


def test_v112m_phase_charter_v1_opens_only_for_mixed_target() -> None:
    result = V112MPhaseCharterAnalyzer().analyze(
        prior_phase_payload=load_json_report(Path("reports/analysis/v112l_phase_closure_check_v1.json"))
    )
    assert result.summary["ready_for_inner_draft_next"] is True
    assert "formal label split" in " ".join(result.out_of_scope)
