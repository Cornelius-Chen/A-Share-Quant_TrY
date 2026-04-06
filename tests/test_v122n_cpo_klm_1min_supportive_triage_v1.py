from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v122n_cpo_klm_1min_supportive_triage_v1 import (
    V122NCpoKlm1MinSupportiveTriageAnalyzer,
    write_report,
)


def test_v122n_cpo_klm_1min_supportive_triage(tmp_path: Path) -> None:
    analyzer = V122NCpoKlm1MinSupportiveTriageAnalyzer()
    result = analyzer.analyze()
    output = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122n_cpo_klm_1min_supportive_triage_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["supportive_continuation_status"] == "explanatory_only"
    with output.open("r", encoding="utf-8") as handle:
        written = json.load(handle)
    assert written["summary"]["recommended_next_posture"] == "recenter_1min_plane_on_downside_reduce_close_microstructure"
