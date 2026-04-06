from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ip_commercial_aerospace_io_evidence_source_direction_triage_v1 import (
    V134IPCommercialAerospaceIOEvidenceSourceDirectionTriageV1Analyzer,
)


def test_v134ip_evidence_source_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134IPCommercialAerospaceIOEvidenceSourceDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["current_local_route_exhausted"] is True
    assert (
        result.summary["authoritative_status"]
        == "retain_true_selection_block_and_shift_next_work_toward_evidence_source_expansion"
    )
    triage_by_target = {row["next_target"]: row for row in result.triage_rows}
    assert triage_by_target["current_named_universe_retuning"]["direction"] == "deprioritize_as_locally_exhausted"
