from pathlib import Path

from a_share_quant.strategy.v113e_pilot_protocol_v1 import (
    V113EPilotProtocolAnalyzer,
    load_json_report,
)


def test_v113e_pilot_protocol_v1_selects_cleanest_archetype() -> None:
    result = V113EPilotProtocolAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v113e_phase_charter_v1.json")),
        archetype_usage_payload=load_json_report(Path("reports/analysis/v113d_bounded_archetype_usage_pass_v1.json")),
    )
    assert result.summary["selected_archetype"] == "commercial_space_mainline"
    assert result.summary["label_block_count"] == 4
