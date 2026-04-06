from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134iv_commercial_aerospace_iu_000738_extension_direction_triage_v1 import (
    V134IVCommercialAerospaceIU000738ExtensionDirectionTriageV1Analyzer,
)


def test_v134iv_000738_extension_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134IVCommercialAerospaceIU000738ExtensionDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["event_backing_present"] is False
    assert (
        result.summary["authoritative_status"]
        == "retain_000738_watch_and_focus_next_on_event_backing_extension"
    )
    triage_by_layer = {row["extension_layer"]: row for row in result.triage_rows}
    assert triage_by_layer["event_backing_extension"]["direction"] == "promote_as_next_missing_evidence_target"
