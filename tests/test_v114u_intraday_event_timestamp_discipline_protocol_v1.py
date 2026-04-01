from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114u_intraday_event_timestamp_discipline_protocol_v1 import (
    V114UIntradayEventTimestampDisciplineProtocolAnalyzer,
)


def test_v114u_intraday_event_timestamp_discipline_protocol() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114UIntradayEventTimestampDisciplineProtocolAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()

    assert result.summary["objective"] == "make_intraday_learning_and_execution_point_in_time_legal"
    assert any(row["field_name"] == "system_visible_time" for row in result.field_schema_rows)
    assert any(row["granularity_required"] == "second" for row in result.mandatory_timestamp_rows)
    assert any(row["timestamp_rule"] == "system_visible_time_is_authoritative" for row in result.usage_boundary_rows)
