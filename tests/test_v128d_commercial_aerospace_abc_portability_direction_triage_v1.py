from pathlib import Path

from a_share_quant.strategy.v128d_commercial_aerospace_abc_portability_direction_triage_v1 import (
    V128DCommercialAerospaceABCPortabilityDirectionTriageAnalyzer,
)


def test_v128d_portability_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V128DCommercialAerospaceABCPortabilityDirectionTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_next_step"] == "main_window_deeper_downside_grammar"
