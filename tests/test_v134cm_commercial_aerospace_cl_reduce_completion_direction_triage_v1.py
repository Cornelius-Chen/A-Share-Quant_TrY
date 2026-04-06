from pathlib import Path

from a_share_quant.strategy.v134cl_commercial_aerospace_reduce_completion_status_audit_v1 import (
    V134CLCommercialAerospaceReduceCompletionStatusAuditV1Analyzer,
    write_report as write_status_report,
)
from a_share_quant.strategy.v134cm_commercial_aerospace_cl_reduce_completion_direction_triage_v1 import (
    V134CMCommercialAerospaceCLReduceCompletionDirectionTriageV1Analyzer,
)


def test_v134cm_commercial_aerospace_cl_reduce_completion_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    status = V134CLCommercialAerospaceReduceCompletionStatusAuditV1Analyzer(repo_root).analyze()
    write_status_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cl_commercial_aerospace_reduce_completion_status_audit_v1",
        result=status,
    )

    result = V134CMCommercialAerospaceCLReduceCompletionDirectionTriageV1Analyzer(repo_root).analyze()
    assert (
        result.summary["authoritative_status"]
        == "freeze_reduce_mainline_as_research_complete_and_leave_only_local_residue_maintenance"
    )
    assert result.summary["remaining_execution_blocker_count"] == 4
    assert result.summary["residue_seed_count"] == 4
