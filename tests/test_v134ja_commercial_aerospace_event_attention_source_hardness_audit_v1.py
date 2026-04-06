from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ja_commercial_aerospace_event_attention_source_hardness_audit_v1 import (
    V134JACommercialAerospaceEventAttentionSourceHardnessAuditV1Analyzer,
)


def test_v134ja_event_attention_source_hardness_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134JACommercialAerospaceEventAttentionSourceHardnessAuditV1Analyzer(repo_root).analyze()

    assert result.summary["symbol_count"] == 5
    assert result.summary["hard_anchor_grade_source_count"] == 1
    assert result.summary["retained_but_non_anchor_source_count"] == 2
    assert result.summary["discarded_or_missing_source_count"] == 2
    assert result.summary["only_hard_anchor_symbol"] == "000547"

    by_symbol = {row["symbol"]: row for row in result.source_rows}
    assert by_symbol["000547"]["source_hardness"] == "hard_anchor_grade_source"
    assert by_symbol["603601"]["source_hardness"] == "retained_continuation_support_source"
    assert by_symbol["300342"]["source_hardness"] == "discarded_theme_heat_source"
    assert by_symbol["002361"]["source_hardness"] == "no_retained_event_source"
