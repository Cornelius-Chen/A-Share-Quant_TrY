from pathlib import Path

from a_share_quant.strategy.v112as_cpo_bounded_implementation_backfill_v1 import (
    V112ASCPOBoundedImplementationBackfillAnalyzer,
)
from a_share_quant.strategy.v112as_phase_charter_v1 import load_json_report


def test_v112as_backfill_applies_all_patch_rules() -> None:
    analyzer = V112ASCPOBoundedImplementationBackfillAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112as_phase_charter_v1.json")),
        patch_spec_payload=load_json_report(Path("reports/analysis/v112ar_cpo_feature_implementation_patch_spec_v1.json")),
        dataset_assembly_payload=load_json_report(Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
    )
    assert result.summary["patch_rule_count_applied"] == 6
    assert result.summary["board_backfill_coverage_ratio"] == 1.0
    assert result.summary["calendar_backfill_coverage_ratio"] == 1.0
