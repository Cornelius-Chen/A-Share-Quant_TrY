from pathlib import Path

from a_share_quant.strategy.v133m_commercial_aerospace_intraday_execution_build_protocol_v1 import (
    V133MCommercialAerospaceIntradayExecutionBuildProtocolAnalyzer,
)


def test_v133m_commercial_aerospace_intraday_execution_build_protocol_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133MCommercialAerospaceIntradayExecutionBuildProtocolAnalyzer(repo_root).analyze()

    assert report.summary["blocked_requirement_count"] == 3
    assert report.summary["workstream_count"] == 3
    assert report.workstream_rows[0]["workstream"] == "point_in_time_intraday_visibility"
    assert report.workstream_rows[1]["workstream"] == "intraday_execution_simulation_surface"
    assert report.workstream_rows[2]["workstream"] == "separate_intraday_replay_lane"
