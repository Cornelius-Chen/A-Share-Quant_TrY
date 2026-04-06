from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v122u_cpo_1min_downside_attachment_stopline_v1 import (
    V122UCpo1MinDownsideAttachmentStoplineAnalyzer,
    write_report,
)


def test_v122u_cpo_1min_downside_attachment_stopline(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports" / "analysis"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "v122s_cpo_1min_historical_bridge_overlap_audit_v1.json").write_text(
        json.dumps({"summary": {"direct_historical_bridge_allowed": False}}), encoding="utf-8"
    )
    (reports_dir / "v122t_cpo_1min_downside_same_plane_stack_audit_v1.json").write_text(
        json.dumps({"summary": {"stack_improves_over_base": False}}), encoding="utf-8"
    )

    analyzer = V122UCpo1MinDownsideAttachmentStoplineAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=reports_dir,
        report_name="v122u_cpo_1min_downside_attachment_stopline_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["attachment_posture"].startswith("defer_")
