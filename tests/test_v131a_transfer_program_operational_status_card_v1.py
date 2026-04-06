from pathlib import Path

from a_share_quant.strategy.v131a_transfer_program_operational_status_card_v1 import (
    V131ATransferProgramOperationalStatusCardAnalyzer,
)


def test_v131a_transfer_program_operational_status_card_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131ATransferProgramOperationalStatusCardAnalyzer(repo_root).analyze()

    assert result.summary["program_status"] == "frozen"
    assert result.summary["rerun_required"] is False
    assert result.summary["nearest_candidate_sector_id"] == "BK0808"
    assert result.summary["decisive_watch_symbol"] == "600118"
