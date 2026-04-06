from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v122h_cpo_recent_1min_proxy_action_timepoint_label_base_v1 import (
    V122HCpoRecent1MinProxyActionTimepointLabelBaseAnalyzer,
)
from a_share_quant.strategy.v122j_cpo_1min_supportive_family_proxy_label_audit_v1 import (
    V122JCpo1MinSupportiveFamilyProxyLabelAuditAnalyzer,
)
from a_share_quant.strategy.v122l_cpo_1min_supportive_add_vs_reduce_separation_discovery_v1 import (
    V122LCpo1MinSupportiveAddVsReduceSeparationDiscoveryAnalyzer,
    write_report,
)
from tests.test_v122e_cpo_1min_supportive_quality_discovery_v1 import _write_minimal_supportive_fixture


def test_v122l_cpo_1min_supportive_add_vs_reduce_separation_discovery(tmp_path: Path) -> None:
    _write_minimal_supportive_fixture(tmp_path)
    V122HCpoRecent1MinProxyActionTimepointLabelBaseAnalyzer(repo_root=tmp_path).analyze()
    V122JCpo1MinSupportiveFamilyProxyLabelAuditAnalyzer(repo_root=tmp_path).analyze()
    analyzer = V122LCpo1MinSupportiveAddVsReduceSeparationDiscoveryAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122l_cpo_1min_supportive_add_vs_reduce_separation_discovery_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["sample_count"] >= 0
