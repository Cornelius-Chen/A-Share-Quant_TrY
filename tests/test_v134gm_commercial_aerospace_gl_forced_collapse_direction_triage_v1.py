from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gl_commercial_aerospace_forced_single_slot_collapse_audit_v1 import (
    V134GLCommercialAerospaceForcedSingleSlotCollapseAuditV1Analyzer,
)
from a_share_quant.strategy.v134gm_commercial_aerospace_gl_forced_collapse_direction_triage_v1 import (
    V134GMCommercialAerospaceGLForcedCollapseDirectionTriageV1Analyzer,
)


def test_v134gm_forced_collapse_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = V134GLCommercialAerospaceForcedSingleSlotCollapseAuditV1Analyzer(repo_root).analyze()
    audit_path = (
        repo_root / "reports" / "analysis" / "v134gl_commercial_aerospace_forced_single_slot_collapse_audit_v1.json"
    )
    audit_path.write_text(json.dumps(audit.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134GMCommercialAerospaceGLForcedCollapseDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["preferred_surrogate_slot"] == "reset_slot"
    assert result.summary["preferred_surrogate_symbol"] == "002085"
    assert result.summary["reset_higher_metric_count"] == 3
    assert result.summary["continuation_higher_metric_count"] == 1

    triage = {row["component"]: row for row in result.triage_rows}
    assert triage["forced_collapse_surrogate"]["status"] == "retain_as_reset_only"
    assert triage["continuation_slot"]["status"] == "retain_as_companion_only"
    assert triage["portable_single_slot_template"]["status"] == "still_blocked"
    assert triage["execution_single_slot_rule"]["status"] == "still_blocked"

    report_path = (
        repo_root / "reports" / "analysis" / "v134gm_commercial_aerospace_gl_forced_collapse_direction_triage_v1.json"
    )
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
