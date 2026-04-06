from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v117l_cpo_human_heuristic_signal_quantization_protocol_v1 import (
    V117LCpoHumanHeuristicSignalQuantizationProtocolAnalyzer,
)


def test_v117l_human_heuristic_quantization_protocol() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117LCpoHumanHeuristicSignalQuantizationProtocolAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
    )

    assert result.summary["heuristic_family_count"] == 4
    assert result.summary["allow_interaction_terms"] is True
