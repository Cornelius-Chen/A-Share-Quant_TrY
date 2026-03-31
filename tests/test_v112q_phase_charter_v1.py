from pathlib import Path

from a_share_quant.strategy.v112q_phase_charter_v1 import (
    V112QPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112q_phase_charter_opens_after_v112p_closure() -> None:
    analyzer = V112QPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112p_phase_closure_payload=load_json_report(Path("reports/analysis/v112p_phase_closure_check_v1.json")),
        owner_requires_schema_hardening=True,
        owner_requires_pre_rise_window=True,
        owner_allows_parallel_collection_drafts=True,
    )

    assert result.summary["do_open_v112q_now"] is True
    assert result.summary["recommended_first_action"] == "freeze_v112q_cpo_information_registry_schema_v1"
