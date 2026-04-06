from pathlib import Path

from a_share_quant.strategy.v124q_commercial_aerospace_universe_triage_v1 import (
    V124QCommercialAerospaceUniverseTriageAnalyzer,
)


def test_v124q_machine_triage_keeps_web_only_names_pending() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V124QCommercialAerospaceUniverseTriageAnalyzer(repo_root).analyze()

    assert result.summary["control_eligible_count"] >= 2
    pending_symbols = {row["symbol"] for row in result.pending_rows}
    assert "002565" in pending_symbols
    control_symbols = {row["symbol"] for row in result.control_eligible_rows}
    assert "002085" in control_symbols
