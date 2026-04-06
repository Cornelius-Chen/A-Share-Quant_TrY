from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v122e_cpo_1min_supportive_quality_discovery_v1 import (
    V122ECpo1MinSupportiveQualityDiscoveryAnalyzer,
    write_report as write_discovery_report,
)
from a_share_quant.strategy.v122f_cpo_1min_supportive_quality_time_split_audit_v1 import (
    V122FCpo1MinSupportiveQualityTimeSplitAuditAnalyzer,
    write_report,
)
from tests.test_v122e_cpo_1min_supportive_quality_discovery_v1 import _write_minimal_supportive_fixture


def test_v122f_cpo_1min_supportive_quality_time_split_audit(tmp_path: Path) -> None:
    _write_minimal_supportive_fixture(tmp_path)
    discovery = V122ECpo1MinSupportiveQualityDiscoveryAnalyzer(repo_root=tmp_path).analyze()
    write_discovery_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122e_cpo_1min_supportive_quality_discovery_v1",
        result=discovery,
    )
    analyzer = V122FCpo1MinSupportiveQualityTimeSplitAuditAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122f_cpo_1min_supportive_quality_time_split_audit_v1",
        result=result,
    )
    assert output_path.exists()
    assert result.summary["split_count"] >= 1
