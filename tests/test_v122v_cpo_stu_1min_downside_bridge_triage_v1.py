from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v122v_cpo_stu_1min_downside_bridge_triage_v1 import (
    V122VCpoStu1MinDownsideBridgeTriageAnalyzer,
    write_report,
)


def test_v122v_cpo_stu_1min_downside_bridge_triage(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports" / "analysis"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "v122s_cpo_1min_historical_bridge_overlap_audit_v1.json").write_text(
        json.dumps({"summary": {"overlap_day_count": 0}}), encoding="utf-8"
    )
    (reports_dir / "v122t_cpo_1min_downside_same_plane_stack_audit_v1.json").write_text(
        json.dumps(
            {
                "summary": {
                    "base_discovery_gap": 0.1,
                    "stack_discovery_gap": 0.11,
                    "base_time_split_mean": 0.52,
                    "stack_time_split_mean": 0.51,
                }
            }
        ),
        encoding="utf-8",
    )
    (reports_dir / "v122u_cpo_1min_downside_attachment_stopline_v1.json").write_text(
        json.dumps({"summary": {"attachment_posture": "defer"}}), encoding="utf-8"
    )

    analyzer = V122VCpoStu1MinDownsideBridgeTriageAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=reports_dir,
        report_name="v122v_cpo_stu_1min_downside_bridge_triage_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["authoritative_status"] == "keep_standalone_soft_component_only"
