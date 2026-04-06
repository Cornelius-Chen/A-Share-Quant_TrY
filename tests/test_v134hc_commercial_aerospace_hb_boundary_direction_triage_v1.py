from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134hb_commercial_aerospace_derivation_boundary_classification_audit_v1 import (
    V134HBCommercialAerospaceDerivationBoundaryClassificationAuditV1Analyzer,
)
from a_share_quant.strategy.v134hc_commercial_aerospace_hb_boundary_direction_triage_v1 import (
    V134HCCommercialAerospaceHBBoundaryDirectionTriageV1Analyzer,
)


def test_v134hc_boundary_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = V134HBCommercialAerospaceDerivationBoundaryClassificationAuditV1Analyzer(repo_root).analyze()
    audit_path = repo_root / "reports" / "analysis" / "v134hb_commercial_aerospace_derivation_boundary_classification_audit_v1.json"
    audit_path.write_text(json.dumps(audit.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134HCCommercialAerospaceHBBoundaryDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["boundary_classification"] == "lockout_aligned_derivation_boundary"
    assert result.summary["derived_stop_matches_lockout_end"] is True
    assert result.summary["raw_coverage_beyond_derived"] is True

    rows = {row["component"]: row for row in result.triage_rows}
    assert rows["raw_data_coverage"]["status"] == "retain"
    assert rows["execution_history_cutoff"]["status"] == "not_primary_blocker"
    assert rows["lockout_aligned_derivation_boundary"]["status"] == "dominant_reading"
    assert rows["shadow_bridge"]["status"] == "keep_blocked"

    report_path = repo_root / "reports" / "analysis" / "v134hc_commercial_aerospace_hb_boundary_direction_triage_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
