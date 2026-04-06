from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v122k_cpo_hij_1min_proxy_label_triage_v1 import (
    V122KCpoHij1MinProxyLabelTriageAnalyzer,
    write_report,
)


def test_v122k_cpo_hij_1min_proxy_label_triage(tmp_path: Path) -> None:
    analyzer = V122KCpoHij1MinProxyLabelTriageAnalyzer()
    result = analyzer.analyze()
    output = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122k_cpo_hij_1min_proxy_label_triage_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["supportive_continuation_status"] == "candidate_family_only"
    with output.open("r", encoding="utf-8") as handle:
        written = json.load(handle)
    assert written["summary"]["recommended_next_posture"] == "run_supportive_family_add_vs_reduce_separation_audit"
