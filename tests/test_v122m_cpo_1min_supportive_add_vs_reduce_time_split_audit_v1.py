from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v122h_cpo_recent_1min_proxy_action_timepoint_label_base_v1 import (
    V122HCpoRecent1MinProxyActionTimepointLabelBaseAnalyzer,
)
from a_share_quant.strategy.v122m_cpo_1min_supportive_add_vs_reduce_time_split_audit_v1 import (
    V122MCpo1MinSupportiveAddVsReduceTimeSplitAuditAnalyzer,
    write_report,
)
from tests.test_v122e_cpo_1min_supportive_quality_discovery_v1 import _write_minimal_supportive_fixture


def test_v122m_cpo_1min_supportive_add_vs_reduce_time_split_audit(tmp_path: Path) -> None:
    _write_minimal_supportive_fixture(tmp_path)
    V122HCpoRecent1MinProxyActionTimepointLabelBaseAnalyzer(repo_root=tmp_path).analyze()
    analyzer = V122MCpo1MinSupportiveAddVsReduceTimeSplitAuditAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122m_cpo_1min_supportive_add_vs_reduce_time_split_audit_v1",
        result=result,
    )
    assert output.exists()
