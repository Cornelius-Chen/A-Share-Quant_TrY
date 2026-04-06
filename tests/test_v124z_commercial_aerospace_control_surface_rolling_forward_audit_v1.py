from pathlib import Path

from a_share_quant.strategy.v124z_commercial_aerospace_control_surface_rolling_forward_audit_v1 import (
    V124ZCommercialAerospaceControlSurfaceRollingForwardAuditAnalyzer,
)


def test_v124z_has_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V124ZCommercialAerospaceControlSurfaceRollingForwardAuditAnalyzer(repo_root).analyze()
    assert result.summary["row_count"] > 0
