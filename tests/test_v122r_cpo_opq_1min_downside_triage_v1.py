from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v122r_cpo_opq_1min_downside_triage_v1 import (
    V122RCpoOpq1MinDownsideTriageAnalyzer,
    write_report,
)


def test_v122r_cpo_opq_1min_downside_triage(tmp_path: Path) -> None:
    analyzer = V122RCpoOpq1MinDownsideTriageAnalyzer()
    result = analyzer.analyze()
    output = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122r_cpo_opq_1min_downside_triage_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["authoritative_status"] == "soft_component"
    with output.open("r", encoding="utf-8") as handle:
        written = json.load(handle)
    assert written["summary"]["recommended_next_posture"] == "retain_as_1min_downside_soft_penalty_only"
