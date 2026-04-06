from pathlib import Path

from a_share_quant.strategy.v134ii_commercial_aerospace_symbol_followthrough_supervision_audit_v1 import (
    V134IICommercialAerospaceSymbolFollowthroughSupervisionAuditV1Analyzer,
)


def test_v134ii_symbol_followthrough_supervision_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134IICommercialAerospaceSymbolFollowthroughSupervisionAuditV1Analyzer(repo_root).analyze()

    assert report.summary["symbol_count"] == 4
    assert report.summary["persistent_followthrough_count"] == 1
    assert report.summary["moderate_followthrough_count"] == 2
    assert report.summary["weak_followthrough_count"] == 1
    rows = {row["symbol"]: row["followthrough_label"] for row in report.followthrough_rows}
    assert rows["603601"] == "persistent_symbol_followthrough_without_board_unlock"
    assert rows["301306"] == "moderate_symbol_followthrough_without_board_unlock"
