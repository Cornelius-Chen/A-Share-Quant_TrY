from __future__ import annotations

import pytest

from a_share_quant.strategy.refresh_trigger_intake import RefreshTriggerIntakeBuilder


def test_refresh_trigger_intake_builder_normalizes_scope() -> None:
    record = RefreshTriggerIntakeBuilder().build(
        trigger_name="new_archetype_gap",
        trigger_type="archetype_gap",
        source="manual_review",
        rationale="Found a materially different suspect geography.",
        datasets=["market_research_v1", "market_research_v1", "market_research_v2_seed"],
        symbols=["603986", "603986", "300502"],
        slices=["2024_q3", "2024_q4", "2024_q4"],
    )

    assert record.summary["trigger_name"] == "new_archetype_gap"
    assert record.summary["dataset_count"] == 2
    assert record.summary["symbol_count"] == 2
    assert record.summary["slice_count"] == 2
    assert record.summary["recommended_next_step"] == "rerun_phase_guard_after_persisting_new_signal"
    affected_scope = record.evidence[1]["actual"]
    assert affected_scope["datasets"] == ["market_research_v1", "market_research_v2_seed"]
    assert affected_scope["symbols"] == ["300502", "603986"]
    assert affected_scope["slices"] == ["2024_q3", "2024_q4"]


def test_refresh_trigger_intake_builder_rejects_unknown_trigger_type() -> None:
    with pytest.raises(ValueError, match="Unsupported trigger_type"):
        RefreshTriggerIntakeBuilder().build(
            trigger_name="weird_signal",
            trigger_type="free_text_maybe",
            source="manual_review",
            rationale="Trying an unsupported trigger label.",
            datasets=["market_research_v1"],
            symbols=["603986"],
            slices=["2024_q4"],
        )
