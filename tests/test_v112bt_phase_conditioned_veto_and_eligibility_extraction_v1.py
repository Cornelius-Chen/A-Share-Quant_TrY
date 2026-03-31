from pathlib import Path

from a_share_quant.strategy.v112bt_phase_conditioned_veto_and_eligibility_extraction_v1 import (
    V112BTPhaseConditionedVetoAndEligibilityExtractionAnalyzer,
    load_json_report,
)


def test_v112bt_extraction_runs() -> None:
    analyzer = V112BTPhaseConditionedVetoAndEligibilityExtractionAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bt_phase_charter_v1.json")),
        bs_refinement_payload=load_json_report(Path("reports/analysis/v112bs_penalized_target_mapping_refinement_v1.json")),
        bp_fusion_payload=load_json_report(Path("reports/analysis/v112bp_cpo_selector_maturity_fusion_pilot_v1.json")),
    )
    assert result.summary["entry_veto_count"] >= 1
    assert result.summary["holding_veto_count"] >= 1
