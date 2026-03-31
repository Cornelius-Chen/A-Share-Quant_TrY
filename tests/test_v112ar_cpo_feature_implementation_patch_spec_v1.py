from pathlib import Path

from a_share_quant.strategy.v112ar_cpo_feature_implementation_patch_spec_v1 import (
    V112ARCPOFeatureImplementationPatchSpecAnalyzer,
)
from a_share_quant.strategy.v112ar_phase_charter_v1 import load_json_report


def test_v112ar_patch_spec_freezes_six_rules() -> None:
    analyzer = V112ARCPOFeatureImplementationPatchSpecAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ar_phase_charter_v1.json")),
        patch_review_payload=load_json_report(Path("reports/analysis/v112aq_cpo_feature_implementation_patch_review_v1.json")),
    )
    assert result.summary["total_patch_rule_count"] == 6
    assert result.summary["next_lawful_move"] == "bounded_implementation_backfill_on_current_truth_rows"
