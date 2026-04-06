from pathlib import Path

from a_share_quant.strategy.v129h_commercial_aerospace_ghi_late_preheat_filter_triage_v1 import (
    V129HCommercialAerospaceGHILatePreheatFilterTriageAnalyzer,
)


def test_v129h_commercial_aerospace_ghi_late_preheat_filter_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129HCommercialAerospaceGHILatePreheatFilterTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] in {
        "promote_late_preheat_filter",
        "keep_current_primary_and_retain_late_preheat_filter_as_supervision_only",
    }
