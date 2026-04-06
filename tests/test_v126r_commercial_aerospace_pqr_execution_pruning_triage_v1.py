from pathlib import Path

from a_share_quant.strategy.v126r_commercial_aerospace_pqr_execution_pruning_triage_v1 import (
    V126RCommercialAerospacePQRExecutionPruningTriageAnalyzer,
)


def test_v126r_execution_pruning_triage_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126RCommercialAerospacePQRExecutionPruningTriageAnalyzer(repo_root).analyze()
    assert result.summary["selected_replay_final_equity"] > 0
