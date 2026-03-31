from pathlib import Path

from a_share_quant.strategy.v112ax_cpo_guarded_branch_admitted_pilot_v1 import (
    V112AXCPOGuardedBranchAdmittedPilotAnalyzer,
    load_json_report,
)


def test_v112ax_guarded_branch_admitted_pilot_stays_stable() -> None:
    analyzer = V112AXCPOGuardedBranchAdmittedPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ax_phase_charter_v1.json")),
        branch_admission_payload=load_json_report(Path("reports/analysis/v112aw_cpo_branch_guarded_admission_review_v1.json")),
        dataset_assembly_payload=load_json_report(Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
    )
    assert result.summary["admitted_branch_row_count"] == 3
    assert result.summary["core_targets_stable_after_guarded_branch_admission"] is True
