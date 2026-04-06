from pathlib import Path

from a_share_quant.strategy.v129p_commercial_aerospace_nop_transfer_preparation_triage_v1 import (
    V129PCommercialAerospaceNOPTransferPreparationTriageAnalyzer,
)


def test_v129p_commercial_aerospace_nop_transfer_preparation_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129PCommercialAerospaceNOPTransferPreparationTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == (
        "start_bk0480_transfer_preparation_with_local_reset_and_keep_bk0808_as_shadow_only"
    )
    assert any(row["direction"] == "bk0480_transfer_preparation" for row in result.direction_rows)
