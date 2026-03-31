from pathlib import Path

from a_share_quant.strategy.v112ai_phase_charter_v1 import (
    V112AIPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112ai_phase_charter_opens_owner_review() -> None:
    analyzer = V112AIPhaseCharterAnalyzer()
    result = analyzer.analyze(
        label_draft_closure_payload=load_json_report(Path("reports/analysis/v112ag_phase_closure_check_v1.json")),
        preservation_rule_payload=load_json_report(Path("reports/analysis/v112ah_factor_candidate_preservation_rule_v1.json")),
    )
    assert result.summary["do_open_v112ai_now"] is True
    assert result.summary["ready_for_owner_review_next"] is True
