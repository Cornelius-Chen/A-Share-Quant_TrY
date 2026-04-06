from pathlib import Path

from a_share_quant.strategy.v123e_cpo_1min_downside_same_plane_integration_audit_v1 import write_report as write_v123e
from a_share_quant.strategy.v123e_cpo_1min_downside_same_plane_integration_audit_v1 import (
    V123ECpo1MinDownsideSamePlaneIntegrationAuditAnalyzer,
)
from a_share_quant.strategy.v123f_cpo_1min_downside_same_plane_stopline_v1 import (
    V123FCpo1MinDownsideSamePlaneStoplineAnalyzer,
)


def test_v123f_blocks_attachment_when_no_material_increment() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    write_v123e(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123e_cpo_1min_downside_same_plane_integration_audit_v1",
        result=V123ECpo1MinDownsideSamePlaneIntegrationAuditAnalyzer(repo_root=repo_root).analyze(),
    )
    result = V123FCpo1MinDownsideSamePlaneStoplineAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["same_plane_attachment_allowed"] is False
