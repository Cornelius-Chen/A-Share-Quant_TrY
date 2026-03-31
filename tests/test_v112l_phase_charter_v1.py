from pathlib import Path

from a_share_quant.strategy.v112l_phase_charter_v1 import V112LPhaseCharterAnalyzer, load_json_report


def test_v112l_phase_charter_v1_opens_owner_review_only() -> None:
    result = V112LPhaseCharterAnalyzer().analyze(
        prior_phase_payload=load_json_report(Path("reports/analysis/v112k_phase_closure_check_v1.json"))
    )
    assert result.summary["ready_for_owner_review_next"] is True
    assert "formal label split" in " ".join(result.out_of_scope)
