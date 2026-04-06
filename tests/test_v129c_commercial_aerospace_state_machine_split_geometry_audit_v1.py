from pathlib import Path

from a_share_quant.strategy.v129c_commercial_aerospace_state_machine_split_geometry_audit_v1 import (
    V129CCommercialAerospaceStateMachineSplitGeometryAuditAnalyzer,
)


def test_v129c_commercial_aerospace_state_machine_split_geometry_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129CCommercialAerospaceStateMachineSplitGeometryAuditAnalyzer(repo_root).analyze()

    assert result.summary["split_count"] == 6
    assert result.summary["authoritative_status"] in {
        "single_split_joint_support_unavailable",
        "single_split_joint_support_available",
    }
    assert len(result.split_rows) == 6
