from pathlib import Path

from a_share_quant.strategy.v127s_commercial_aerospace_rst_pressure_relocation_triage_v1 import (
    V127SCommercialAerospaceRSTPressureRelocationTriageAnalyzer,
)


def test_v127s_pressure_relocation_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127SCommercialAerospaceRSTPressureRelocationTriageAnalyzer(repo_root).analyze()

    assert report.summary["reference_variant"] == "veto_drag_trio_impulse_only"
