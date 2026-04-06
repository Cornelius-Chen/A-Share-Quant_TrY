from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v122h_cpo_recent_1min_proxy_action_timepoint_label_base_v1 import (
    V122HCpoRecent1MinProxyActionTimepointLabelBaseAnalyzer,
)
from a_share_quant.strategy.v122o_cpo_1min_downside_failure_discovery_v1 import (
    V122OCpo1MinDownsideFailureDiscoveryAnalyzer,
    write_report,
)
from tests.test_v122e_cpo_1min_supportive_quality_discovery_v1 import _write_minimal_supportive_fixture


def test_v122o_cpo_1min_downside_failure_discovery(tmp_path: Path) -> None:
    _write_minimal_supportive_fixture(tmp_path)
    V122HCpoRecent1MinProxyActionTimepointLabelBaseAnalyzer(repo_root=tmp_path).analyze()
    analyzer = V122OCpo1MinDownsideFailureDiscoveryAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122o_cpo_1min_downside_failure_discovery_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["sample_count"] >= 0
