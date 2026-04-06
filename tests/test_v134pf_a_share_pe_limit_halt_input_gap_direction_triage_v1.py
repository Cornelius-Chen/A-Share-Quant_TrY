from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pf_a_share_pe_limit_halt_input_gap_direction_triage_v1 import (
    V134PFASharePELimitHaltInputGapDirectionTriageV1Analyzer,
)


def test_v134pf_limit_halt_input_gap_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PFASharePELimitHaltInputGapDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "limit_halt_derivation_requires_semantic_side_inputs_not_more_price_only_raw"
    )


def test_v134pf_limit_halt_input_gap_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PFASharePELimitHaltInputGapDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["semantic_side_inputs"]["direction"].startswith("add_board_st_and_suspension_side_inputs")
