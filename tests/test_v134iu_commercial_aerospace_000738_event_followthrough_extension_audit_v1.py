from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134iu_commercial_aerospace_000738_event_followthrough_extension_audit_v1 import (
    V134IUCommercialAerospace000738EventFollowthroughExtensionAuditV1Analyzer,
)


def test_v134iu_000738_event_followthrough_extension_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134IUCommercialAerospace000738EventFollowthroughExtensionAuditV1Analyzer(repo_root).analyze()

    assert result.summary["symbol"] == "000738"
    assert result.summary["event_backing_present"] is False
    assert result.summary["local_rebound_leadership_day_count"] == 3
    assert result.summary["followthrough_extension_label"] == "moderate_but_not_persistent"

    by_layer = {row["extension_layer"]: row for row in result.extension_rows}
    assert by_layer["event_backing_extension"]["current_status"] == "still_absent"
    assert by_layer["local_rebound_leadership_extension"]["current_status"] == "explicitly_present"
    assert by_layer["followthrough_extension"]["current_status"] == "moderate_but_not_persistent"
