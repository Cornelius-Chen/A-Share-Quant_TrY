from pathlib import Path

from a_share_quant.strategy.v112n_phase_charter_v1 import V112NPhaseCharterAnalyzer, load_json_report


def test_v112n_phase_charter_v1_opens_review_only_shadow_rerun() -> None:
    result = V112NPhaseCharterAnalyzer().analyze(
        prior_phase_payload=load_json_report(Path("reports/analysis/v112m_phase_closure_check_v1.json"))
    )
    assert result.summary["ready_for_shadow_rerun_next"] is True
    assert "formal label split" in " ".join(result.out_of_scope)
